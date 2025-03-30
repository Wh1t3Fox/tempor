#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rich.table import Table
from os import access, R_OK
from os.path import isfile
import subprocess
import argparse
import json
import sys

from .constant import __version__, provider_info
from .playbook import run_playbook, run_custom_playbook
from .ssh import check_sshkeys, install_ssh_keys
from .console import console
from .utils import (
    find_hostname,
    get_config,
    get_hosts,
    image_region_choices,
    save_hosts
)
from .apis import *
from .tf import *


def get_args() -> tuple[str, str, argparse.Namespace]:

    cfg = get_config()

    if not cfg:
        sys.exit(1)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-t", "--teardown", default=None, help="Name of VPS Image to Tear down"
    )
    parser.add_argument("-u", "--update", action="store_true", help="Check for Upates")
    parser.add_argument("--version", action="store_true", help="Print current version")

    # build args for each provider
    subparsers = parser.add_subparsers(dest="provider")
    for entry in cfg["providers"]:
        provider = entry["name"]
        api_token = entry["api_token"]

        provider_info[provider] = dict()

        # validate API creds
        # only call the APIs once
        if not getattr(globals()[provider], "authorized")(api_token):
            console.print(
                f"[red bold] Invalid {provider} API Token. Fix or remove provider."
            )
            sys.exit(1)

        provider_info[provider]["api_token"] = api_token

        prov_parser = subparsers.add_parser(provider, epilog="", add_help=False)
        prov_parser.add_argument("-h", "--help", action="store_true")
        prov_parser.add_argument(
            "-c",
            "--count",
            type=int,
            default=1,
            help="Number of images to create",
        )
        prov_parser.add_argument(
            "--image",
            metavar="image",
            help="Specify the OS image",
        )
        prov_parser.add_argument(
            "--region",
            metavar="region",
            help="Specify the region to host the image",
        )
        prov_parser.add_argument(
            "--resources",
            metavar="resources",
            help="Specify the hardware resources for the host image",
        )
        prov_parser.add_argument(
            "-s", "--setup", action="store_true", default=False, help="Create a VPS"
        )
        prov_parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            default=False,
            help="List Available VPS'",
        )
        prov_parser.add_argument(
            "-m",
            "--minimal",
            action="store_true",
            default=False,
            help="Minimal Configuration (just configs)",
        )
        prov_parser.add_argument(
            "-f",
            "--full",
            action="store_true",
            default=False,
            help="Full Configuration with hardening",
        )
        prov_parser.add_argument(
            "--no-config",
            action="store_true",
            help="Do not run any configuration (except custom)",
        )
        prov_parser.add_argument(
            "--custom",
            type=str,
            default=False,
            help="Specify Ansible playbook for custom configuration (Path to main.yml file)",
        )
        if provider == "aws":
            prov_parser.add_argument(
                "-t",
                "--tags",
                type=json.loads,
                default="{}",
                metavar="tags",
                help="Tags to add to the instance",
            )

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    elif args.update:
        console.print("Checking for updates...")
        res = subprocess.check_output(
            ["python3", "-m", "pip", "list", "--outdated", "--not-required"],
            stderr=subprocess.DEVNULL,
        ).decode()

        if parser.prog in res:
            offset = res.find(parser.prog)
            res = res[offset:]
            _name, _, c_ver, _, _, l_ver, _ = res.split(" ", 6)
            console.print(f"[green]Version {l_ver} available!")
            choice = input("Would you like to update? (Y/n)")
            if choice.lower() == "y" or choice == "":
                subprocess.check_output(
                    ["python3", "-m", "pip", "install", "-U", "tempor"],
                    stdout=subprocess.DENVULL,
                    stderr=subprocess.DEVNULL,
                )
        else:
            console.print("Running latest version.")
        sys.exit(0)

    elif args.teardown:
        return args

    # not specifying anything other than setup parse config
    if args.setup and not (args.minimal or args.full or args.custom):
        if args.no_config:
            args.minimal = False
            args.full = False

        if "config" in cfg:
            # This is default behavior so don't really have to do this
            # first set is mutually exclusive, but custom can be used with any
            if "none" in cfg["config"] and cfg["config"]["none"] is True:
                args.no_config = True
            elif "bare" in cfg["config"] and cfg["config"]["bare"] is True:
                args.minimal = False
                args.full = False
            elif "minimal" in cfg["config"] and cfg["config"]["minimal"] is True:
                args.minimal = True
                args.full = False
            elif "full" in cfg["config"] and cfg["config"]["minimal"] is True:
                args.minimal = False
                args.full = False
                args.minimal = False
                args.full = True
            elif (
                ("bare" in cfg["config"] and cfg["config"]["bare"] is False)
                and ("minimal" in cfg["config"] and cfg["config"]["minimal"] is False)
                and ("full" in cfg["config"] and cfg["config"]["minimal"] is False)
            ):
                args.no_config = True

            if "custom" in cfg["config"]:
                args.minimal = False
                args.full = False
                args.custom = cfg["config"]["custom"]

    if args.custom:
        file = args.custom
        assert isfile(file) and access(
            file, R_OK
        ), f"File {file} doesn't exist or isn't readable"

    # check options for this provider
    for p in cfg["providers"]:
        if p["name"] == args.provider:

            if "image" in p and not args.image:
                args.image = p["image"]

            # GCP only
            if "zone" in p and not args.zone:
                args.zone = p["zone"]

            if "region" in p and not args.region:
                args.region = p["region"]

            if "resources" in p and not args.resources:
                args.resources = p["resources"]

            if "api_token" in p:
                args.api_token = p["api_token"]
            break
    else:
        parser.print_help()
        parser.exit(0)
        sys.exit(1)

    provider_info[args.provider]["regions"] = getattr(
        globals()[args.provider], "get_regions"
    )(args.api_token)

    if args.provider == "azure" or args.provider == "aws":
        provider_info[args.provider]["images"] = getattr(
            globals()[args.provider], "get_images"
        )(args.api_token, args.region)
        provider_info[args.provider]["resources"] = getattr(
            globals()[args.provider], "get_resources"
        )(args.api_token, args.region)
    elif args.provider == "gcp":
        # make sure the image/region combo is allowed
        valid_zone = getattr(globals()[args.provider], "valid_zone")(
            args.api_token, args.zone
        )
        assert valid_zone, f"{args.zone} is not valid"

        provider_info[args.provider]["images"] = getattr(
            globals()[args.provider], "get_images"
        )(args.api_token)
        provider_info[args.provider]["resources"] = getattr(
            globals()[args.provider], "get_resources"
        )(args.api_token, args.zone)
    else:
        provider_info[args.provider]["images"] = getattr(
            globals()[args.provider], "get_images"
        )(args.api_token)
        provider_info[args.provider]["resources"] = getattr(
            globals()[args.provider], "get_resources"
        )(args.api_token)

    if args.image not in provider_info[args.provider]["images"]:
        console.print(f"[red bold]{args.image} is not a supported image")
        parser.print_help()
        image_region_choices(args.provider)
        parser.exit(0)

    if args.region not in provider_info[args.provider]["regions"]:
        console.print(f"[red bold]{args.region} is not a supported region")
        parser.print_help()
        image_region_choices(args.provider)
        parser.exit(0)

    # make sure the image/region combo is allowed
    valid_image = getattr(globals()[args.provider], "valid_image_in_region")(
        args.image, args.region, args.api_token
    )
    assert valid_image, f"{args.image} is not available in {args.region}"

    # make sure the CPU RAM resources are allowed in this region
    valid_resources = getattr(globals()[args.provider], "valid_resource_in_region")(
        args.resources, args.region, args.api_token
    )
    assert valid_resources, f"{args.resources} is not available in {args.region}"

    try:
        if args.help:
            image_region_choices(args.provider)
            parser.exit(0)

        # configure some easier options
        if not args.setup and (args.full or args.minimal):
            args.setup = True

        if args.provider == "aws":
            args.user = aws.get_user(args.image)
        else:
            args.user = "root"
    except AttributeError as e:  # typically thrown at the args.help
        console.print(e)
        parser.print_help()
        parser.exit(0)

    return args


def main(args: argparse.Namespace = None, override_teardown: bool = False) -> None:
    if not args:
        args = get_args()

    # if teardown we need to look up some info
    if args.teardown:
        args.list = False
        _host = find_hostname(args.teardown)

        if not _host:
            console.print(f"[red bold]{args.teardown} is not a valid hostname")
            return None

        _provider, _, _image = _host["workspace"].replace("+", "/").split("_")
        args.provider = _provider
        args.image = _image
        args.region = _host["region"]
        args.api_token = provider_info[args.provider]["api_token"]

    tf = TF(args.provider, args.region, args.image, args.api_token)

    tf_workspace_name = tf.get_workspace_name()

    if override_teardown:
        args.teardown = tf_workspace_name
        args.setup = False

    # make sure we have the correct workspace, and create it if it does not exist
    if not tf.correct_workspace() and not args.list:
        tf.setup_workspace()
    elif not (args.teardown or args.list):
        # Only 1 provider/region/image at a time
        console.print(
            "[red bold]Provider/Region/Image Combination taken. Chose a different region, image, or provider."
        )
        return

    # now what do we want to do?
    if args.teardown:
        console.print(f"Tearing down {args.teardown}...", end="", style="bold italic")
        tf.teardown(args.teardown)
        return

    elif args.list:
        all_hosts = get_hosts()

        if args.provider in all_hosts:
            table = Table(title="Active VPS'")
            table.add_column("VPS Name", style="cyan")
            table.add_column("IP Address", style="magenta")
            table.add_column("Region", style="magenta")
            table.add_column("Image", style="magenta")
            table.add_column("Hardware", style="magenta")

            for host in all_hosts[args.provider]:
                for hostname, values in host.items():
                    ip = values["ip"] if "ip" in values else "UNK"
                    region = values["region"] if "region" in values else "UNK"
                    image = (
                        values["workspace"].split("_")[-1].replace("+", "/")
                        if "workspace" in values
                        else "UNK"
                    )
                    resources = values["resources"] if "resources" in values else "UNK"

                    table.add_row(hostname, ip, region, image, resources)
            console.print(table)
        return


    # prevent accidental creations
    if not args.setup:
        return


    # lets plan the config
    console.print("Preparing Configuration...", end="", style="bold italic")
    if not tf.plan(args.count):
        # if plan fails -- teardown
        main(args, True)
    console.print("Done.")


    # now apply the config
    console.print("Creating VPS...", end="", style="bold italic")
    if not tf.apply():
        # if apply fails -- teardown
        main(args, True)
    console.print("Done.")


    console.print("Configuring SSH Keys...", end="", style="bold italic")
    # Creates new key pair
    if check_sshkeys(args.provider, args.region, args.image) is False:
        return

    # Get Hostname and IP Adress
    output = tf.get_output()
    # digitalocean
    if "droplet_ip_address" in output:
        for hostname, ip_address in output["droplet_ip_address"]["value"].items():
            new_hosts = dict()
            new_hosts[hostname] = {
                "ip": ip_address,
                "region": args.region,
                "resources": args.resources,
                "workspace": tf_workspace_name,
            }
            install_ssh_keys(
                args.provider, args.region, args.image, hostname, ip_address, args.user
            )
            save_hosts(args.provider, new_hosts)

    # linode, aws
    elif "instance_ip_address" in output:
        for hostname, ip_address in output["instance_ip_address"]["value"].items():
            new_hosts = dict()
            new_hosts[hostname] = {
                "ip": ip_address,
                "region": args.region,
                "resources": args.resources,
                "workspace": tf_workspace_name,
            }
            install_ssh_keys(
                args.provider, args.region, args.image, hostname, ip_address, args.user
            )
            save_hosts(args.provider, new_hosts)

    # vultr
    elif "server_ip_address" in output:
        for hostname, ip_address in output["server_ip_address"]["value"].items():
            new_hosts = dict()
            new_hosts[hostname] = {
                "ip": ip_address,
                "region": args.region,
                "resources": args.resources,
                "workspace": tf_workspace_name,
            }
            install_ssh_keys(
                args.provider, args.region, args.image, hostname, ip_address, args.user
            )
            save_hosts(args.provider, new_hosts)
    console.print("Done.")

    if args.no_config:
        pass
    # Ansible configuration
    elif args.full:
        run_playbook("full.yml", args.user)
    elif args.minimal:
        run_playbook("minimal.yml", args.user)
    else:
        run_playbook("bare.yml", args.user)

    if args.custom:
        run_custom_playbook(args.custom, args.user)

    console.print("\nVPS' now available!\n", style="bold italic green")


if __name__ == "__main__":
    main()
