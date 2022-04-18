#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import *
from rich.console import Console
from rich.table import Table
from rich.progress import track
import argparse
import time
import json
import sys
import os

from tempor import ROOT_DIR
from tempor.console import console
from tempor.ssh import check_sshkeys, install_ssh_keys
from tempor.utils import (
    get_config,
    get_hosts,
    rm_hosts,
    save_hosts,
    terraform_installed,
)
from tempor.playbook import run_playbook


def get_args():
    cfg = get_config()

    if not cfg:
        sys.exit(1)

    if "default" in cfg:
        provider = cfg["default"]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--provider",
        default=provider,
        choices=os.listdir(f"{ROOT_DIR}/providers"),
        help="Specify the Provider Name",
    )
    parser.add_argument(
        "-c", "--count", default=1, type=int, help="Number of VPS' to Create"
    )
    parser.add_argument("--setup", action="store_true", help="Create VPS'")
    parser.add_argument("--list", action="store_true", help="List Available VPS'")
    parser.add_argument(
        "--no-config", action="store_true", help="Leave as a Bare Install"
    )
    parser.add_argument("--teardown", action="store_true", help="Tear down VPS'")

    args = parser.parse_args()

    # Check if provider is set
    if not args.provider:
        console.print("[red bold]Must Specify a Provider")
        sys.exit(1)

    provider = args.provider
    if "providers" in cfg:
        # lets check for the API token
        try:
            api_token = [
                i["api_token"] for i in cfg["providers"] if i["name"] == provider
            ][0]
        except IndexError:
            console.print("[red bold]API Tokens are required")
            sys.exit(1)
    else:
        console.print("[red bold]Providers are required")
        sys.exit(1)

    return (provider, api_token, args)


def main():
    provider, api_token, args = get_args()
    plan_path = f"{ROOT_DIR}/providers/{provider}/files/plan"
    terr_path = terraform_installed()
    if terr_path is None:
        console.print("[red bold]Platform not Supported")
        return

    t = Terraform(
        working_dir=f"{ROOT_DIR}/providers/{provider}",
        variables={"api_token": api_token},
        terraform_bin_path=terr_path,
    )
    # make sure terraform is initialized
    ret, stdout, stderr = t.init()
    if ret != 0 and stderr:
        console.print("[red bold]Failed during initialization")
        console.print(f"[red bold]{stderr}")
        return

    # now what do we want to do?
    if args.teardown:
        console.print("Tearing down...", end="", style="bold italic")
        ret, stdout, stderr = t.cmd("apply", "-destroy", "-auto-approve", var={"api_token": api_token})
        if ret != 0 and stderr:
            console.print("[red bold]Failed during Teardown")
            console.print(f"[red bold]{stderr}")
        rm_hosts(provider)
        console.print("Done.")
        return

    elif args.list:
        all_hosts = get_hosts()

        if provider in all_hosts:
            table = Table(title="Active VPS'")
            table.add_column("VPS Name", style="cyan")
            table.add_column("IP Address", style="magenta")

            for host, ip in all_hosts[provider].items():
                table.add_row(host, ip)
            console.print(table)
        return

    # prevent accidental creations
    if not args.setup:
        return

    if check_sshkeys(provider) is False:
        return

    # lets plan the config
    console.print("Preparing Configuration...", end="", style="bold italic")
    ret, stdout, stderr = t.cmd(
        "plan", f"-out={plan_path}", var={"api_token": api_token, "num": args.count}
    )
    if ret != 0 and stderr:
        console.print("[red bold]Failed during Planning")
        console.print(f"[red bold]{stderr}")
        return
    console.print("Done.")

    # now apply the config
    console.print("Creating VPS...", end="", style="bold italic")
    ret, stdout, stderr = t.cmd("apply", plan_path)
    if ret != 0 and stderr:
        console.print("[red bold]Failed during Applying")
        console.print(f"[red bold]{stderr}")
        return
    console.print("Done.")

    console.print("Configuring SSH Keys...", end="", style="bold italic")
    # Get Hostname and IP Adress
    output = t.output()

    new_hosts = dict()
    # digitalocean
    if "droplet_ip_address" in output:
        for hostname, ip_address in output["droplet_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)

    # linode
    elif "instance_ip_address" in output:
        for hostname, ip_address in output["instance_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)

    # vultr
    elif "server_ip_address" in output:
        for hostname, ip_address in output["server_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)
    console.print("Done.")

    save_hosts(provider, new_hosts)

    if not args.no_config:
        run_playbook()

    console.print("\nVPS' now available!\n", style="bold italic green")
    for host in new_hosts:
        console.print(f"ssh {host}", style="magenta")


if __name__ == "__main__":
    main()
