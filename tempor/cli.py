#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import *
from rich.console import Console
from rich.table import Table
from rich.progress import track
from pathlib import Path
import argparse
import time
import json
import sys
import re
import os

from tempor import ROOT_DIR
from tempor.apis import *
from tempor.console import console
from tempor.utils import (
    get_config,
    get_hosts,
    rm_hosts,
    save_hosts,
    terraform_installed,
)
from tempor.playbook import run_playbook
from tempor.ssh import check_sshkeys, install_ssh_keys


provider_info = dict()

def image_region_choices(provider):
    if provider is None:
        print(''' ''')
        return

    reg_table = Table(title="Regions")
    reg_table.add_column("ID", style="cyan")
    if provider == 'gcp':
        reg_table.add_column("Zones", style="magenta")
    else:
        reg_table.add_column("Location", style="magenta")

    for _id,name in provider_info[provider]['regions'].items():
        reg_table.add_row(str(_id), str(name))

    img_table = Table(title="Images x86-64")
    img_table.add_column("ID", style="cyan")
    img_table.add_column("Name", style="magenta")
    for _id,name in provider_info[provider]['images'].items():
        img_table.add_row(str(_id), str(name))

    print(f'''
usage: tempor {provider} [-h] [--image image] [--region region] [-s] [-l] [-b] [-m] [--teardown]

options:
  -h, --help       show this help message and exit
  --image image    Specify the OS Image
  --region region  Specify the Region to Host the Image
  -s, --setup      Create VPS'
  -l, --list       List Available VPS'
  -b, --bare       Leave as a Bare Install
  -m, --minimal    Minimal Configuration
  --teardown       Tear down VPS'
''')
    console.print(reg_table)
    console.print(img_table)

def get_args():
    cfg = get_config()

    if not cfg:
        sys.exit(1)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    # build args for each provider
    subparsers = parser.add_subparsers(dest='provider')
    for entry in cfg['providers']:
        provider = entry['name']
        api_token = entry['api_token']

        # validate API creds
        # only call the APIs once
        if not getattr(globals()[provider], 'authorized')(api_token):
            console.print(f"[red bold] Invalid {provider} API Token. Fix or remove provider.")
            sys.exit(1)


        #provider_info[provider] = dict()
        #provider_info[provider]['images'] =  getattr(globals()[provider], 'get_images')(api_token)
        #provider_info[provider]['regions'] =  getattr(globals()[provider], 'get_regions')(api_token)

        prov_parser = subparsers.add_parser(provider, epilog='', add_help=False)
        prov_parser.add_argument(
            "--image",
            metavar = "image",
            #choices = provider_info[provider]['images'].keys(),
            help="Specify the OS Image",
        )
        prov_parser.add_argument(
            "--region",
            metavar = "region",
            #choices = provider_info[provider]['regions'].keys(),
            help="Specify the Region to Host the Image",
        )
        prov_parser.add_argument("-s", "--setup", action="store_true", help="Create VPS'")
        prov_parser.add_argument("-l", "--list", action="store_true", help="List Available VPS'")
        prov_parser.add_argument(
            "-b", "--bare", action="store_true", help="Leave as a Bare Install"
        )
        prov_parser.add_argument(
            "-m", "--minimal", action="store_true", help="Minimal Configuration"
        )
        prov_parser.add_argument("--teardown", action="store_true", help="Tear down VPS'")
        prov_parser.add_argument('-h', '--help', action='store_true')

    
    args = parser.parse_args()

    # Check for a default provider
    if 'default' in cfg and cfg['default']:
        default_provider = cfg['default']
    else:
        default_provider = None

    # if default_provider is not chosen, update settings
    if default_provider != args.provider:
        default_provider = args.provider

    # check options for this provider
    for p in cfg['providers']:
        if p['name'] == default_provider:

            if 'image' in p:
                default_image = p['image']
                if not args.image:
                    args.image = default_image

            if 'region' in p:
                default_region = p['region']
                if not args.region:
                    args.region = default_region

            if 'api_token' in p:
                api_token = p['api_token']
                args.api_token = api_token
            break
    else:
        console.print(f"[red bold]{default_provider} is not a supported provider")
        parser.print_help()
        parser.exit(0)
        sys.exit(1)
    
    provider_info[args.provider] = dict()
    if args.provider == 'azure':
        provider_info[args.provider]['images'] =  getattr(globals()[args.provider], 'get_images')(api_token, args.region)
    else:
        provider_info[args.provider]['images'] =  getattr(globals()[args.provider], 'get_images')(api_token)
    provider_info[args.provider]['regions'] =  getattr(globals()[args.provider], 'get_regions')(api_token)

    if args.image not in provider_info[args.provider]['images']:
        console.print(f"[red bold]{args.image} is not a supported image")
        parser.print_help()
        image_region_choices(args.provider)
        parser.exit(0)

    if args.region not in provider_info[args.provider]['regions']:
        console.print(f"[red bold]{args.region} is not a supported region")
        parser.print_help()
        image_region_choices(args.provider)
        parser.exit(0)

    valid_image = getattr(globals()[args.provider], 'valid_image_in_region')(args.image, args.region, api_token)
    assert valid_image, f"{args.image} is not available in {args.region}"

    try:
        if args.help:
            image_region_choices(args.provider)
            parser.exit(0)

        # configure some easier options
        if not args.setup and (args.bare or args.minimal):
            args.setup = True

        if args.provider == 'aws':
            args.user = 'user'
        else:
            args.user = 'root'
    except AttributeError as e:  # typically thrown at the args.help
        parser.print_help()
        parser.exit(0)


    return (args.provider, api_token, args)


def main(args: argparse.Namespace = None, override_teardown: bool = False):
    if not args:
        provider, api_token, args = get_args()

    if override_teardown:
        provider = args.provider
        api_token = args.api_token
        args.teardown = True
        args.setup = False

    plan_path = f"{ROOT_DIR}/providers/{provider}/files/plans/{args.region}/{args.image}/plan"
    
    plan_parent_path = Path(plan_path).parent.absolute()
    if not os.path.exists(plan_parent_path):
        os.makedirs(plan_parent_path)

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
        ret, stdout, stderr = t.cmd("apply", "-destroy", "-auto-approve", 
                                var={
                                    "api_token": api_token,
                                    "image": args.image,
                                    "region": args.region
                                })
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
            "plan", f"-out={plan_path}", var={
                            "api_token": api_token, 
                            "image": args.image,
                            "region": args.region
                        }
    )
    if ret != 0 and stderr:
        # Fix the color escape sequences
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)
        main(args, True)  # force teardown
        return
    console.print("Done.")

    # now apply the config
    console.print("Creating VPS...", end="", style="bold italic")
    ret, stdout, stderr = t.cmd("apply", plan_path)
    if ret != 0 and stderr:
        # Fix the color escape sequences
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)
        main(args, True)  # force teardown
    console.print("Done.")

    console.print("Configuring SSH Keys...", end="", style="bold italic")
    # Get Hostname and IP Adress
    output = t.output()

    new_hosts = dict()
    # digitalocean
    if "droplet_ip_address" in output:
        for hostname, ip_address in output["droplet_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address, args.user)

    # linode, aws
    elif "instance_ip_address" in output:
        for hostname, ip_address in output["instance_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address, args.user)

    # vultr
    elif "server_ip_address" in output:
        for hostname, ip_address in output["server_ip_address"]["value"].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address, args.user)
    console.print("Done.")

    save_hosts(provider, new_hosts)

    if not args.bare:
        playbook = 'minimal.yml' if args.minimal else 'main.yml'
        run_playbook(playbook, args.user)

    console.print("\nVPS' now available!\n", style="bold italic green")
    for host in new_hosts:
        console.print(f"ssh {host}", style="magenta")


if __name__ == "__main__":
    main()
