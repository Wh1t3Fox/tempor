#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import *
from rich.console import Console
from rich.table import Table
from rich.progress import track
from pathlib import Path
from os import access, R_OK
from os.path import isfile
import argparse
import time
import json
import sys
import re
import os

from tempor import (
    provider_info,
    ROOT_DIR
)
from tempor.apis import (
    aws,
    azure,
    digitalocean,
    gcp,
    linode,
    vultr
)
from tempor.console import console
from tempor.utils import (
    find_hostname,
    get_config,
    get_hosts,
    image_region_choices,
    rm_hosts,
    save_hosts,
    terraform_installed,
)
from tempor.workspaces import *
from tempor.playbook import run_playbook, run_custom_playbook
from tempor.ssh import check_sshkeys, install_ssh_keys


# TODO: cleanup some of this code
def get_args() -> (str, str, argparse.Namespace):

    cfg = get_config()

    if not cfg:
        sys.exit(1)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--teardown", default=None, help="Name of VPS Image to Tear down")

    # build args for each provider
    subparsers = parser.add_subparsers(dest='provider')
    for entry in cfg['providers']:
        provider = entry['name']
        api_token = entry['api_token']

        provider_info[provider] = dict()

        # validate API creds
        # only call the APIs once
        if not getattr(globals()[provider], 'authorized')(api_token):
            console.print(f"[red bold] Invalid {provider} API Token. Fix or remove provider.")
            sys.exit(1)

        provider_info[provider]['api_token'] = api_token


        prov_parser = subparsers.add_parser(provider, epilog='', add_help=False)
        prov_parser.add_argument(
            "--image",
            metavar = "image",
            help="Specify the OS image",
        )
        prov_parser.add_argument(
            "--region",
            metavar = "region",
            help="Specify the region to host the image",
        )
        prov_parser.add_argument(
            "--resources",
            metavar = "resources",
            help="Specify the hardware resources for the host image",
        )
        prov_parser.add_argument("-s", "--setup", action="store_true", default=False, help="Create a VPS")
        prov_parser.add_argument("-l", "--list", action="store_true", default=False, help="List Available VPS'")
        prov_parser.add_argument(
            "-m", "--minimal", action="store_true", default=False, help="Minimal Configuration (just configs)"
        )
        prov_parser.add_argument(
            "-f", "--full", action="store_true", default=False, help="Full Configuration with hardening"
        )
        prov_parser.add_argument(
            "-c", "--custom", type=str, default=False, help="Specify Ansible role for custom configuration (main.yml file)"
        )
        prov_parser.add_argument('-h', '--help', action='store_true')

    
    args = parser.parse_args()

    if args.teardown:
        return args

    if args.custom:
        file = args.custom
        assert isfile(file) and access(file, R_OK), \
       f"File {file} doesn't exist or isn't readable"


    # check options for this provider
    for p in cfg['providers']:
        if p['name'] == args.provider:

            if 'image' in p and not args.image:
                    args.image = p['image']

            # GCP only
            if 'zone' in p and not args.zone:
                args.zone = p['zone']

            if 'region' in p and not args.region:
                args.region = p['region']

            if 'resources' in p and not args.resources:
                args.resources = p['resources']

            if 'api_token' in p:
                args.api_token = p['api_token']
            break
    else:
        console.print(f"[red bold]{default_provider} is not a supported provider")
        parser.print_help()
        parser.exit(0)
        sys.exit(1)
    
    provider_info[args.provider]['regions'] =  getattr(globals()[args.provider], 'get_regions')(args.api_token)

    if args.provider == 'azure' or args.provider == 'aws':
        provider_info[args.provider]['images'] =  getattr(globals()[args.provider], 'get_images')(args.api_token, args.region)
        provider_info[args.provider]['resources'] =  getattr(globals()[args.provider], 'get_resources')(args.api_token, args.region)
    elif args.provider == 'gcp':
        # make sure the image/region combo is allowed 
        valid_zone = getattr(globals()[args.provider], 'valid_zone')(args.api_token, args.zone)
        assert valid_zone, f"{args.zone} is not valid"

        provider_info[args.provider]['images'] =  getattr(globals()[args.provider], 'get_images')(args.api_token)
        provider_info[args.provider]['resources'] =  getattr(globals()[args.provider], 'get_resources')(args.api_token, args.zone)
    else:
        provider_info[args.provider]['images'] =  getattr(globals()[args.provider], 'get_images')(args.api_token)
        provider_info[args.provider]['resources'] =  getattr(globals()[args.provider], 'get_resources')(args.api_token)


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

    # make sure the image/region combo is allowed 
    valid_image = getattr(globals()[args.provider], 'valid_image_in_region')(args.image, args.region, args.api_token)
    assert valid_image, f"{args.image} is not available in {args.region}"

    # make sure the CPU RAM resources are allowed in this region
    valid_resources = getattr(globals()[args.provider], 'valid_resource_in_region')(args.resources, args.region, args.api_token)
    assert valid_resources, f"{args.resources} is not available in {args.region}"


    try:
        if args.help:
            image_region_choices(args.provider)
            parser.exit(0)

        # configure some easier options
        if not args.setup and (args.full or args.minimal):
            args.setup = True

        if args.provider == 'aws':
            args.user = 'user'
        else:
            args.user = 'root'
    except AttributeError as e:  # typically thrown at the args.help
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
            return

        _provider, _, _image = _host['workspace'].replace('+', '/').split('_')
        args.provider = _provider
        args.image = _image
        args.region = _host['region']
        args.api_token = provider_info[args.provider]['api_token']

    plan_path = f"{ROOT_DIR}/providers/{args.provider}/files/plans/{args.region}/{args.image}/plan"
    # The name must contain only URL safe characters, and no path separators.
    tf_workspace_name = f'{args.provider}_{args.region}_{args.image}'.replace('/', '+')

    if override_teardown:
        args.teardown = tf_workspace_name
        args.setup = False
    
    plan_parent_path = Path(plan_path).parent.absolute()
    if not os.path.exists(plan_parent_path):
        os.makedirs(plan_parent_path)

    terr_path = terraform_installed()
    if terr_path is None:
        console.print("[red bold]Platform not Supported")
        return

    t = Terraform(
        working_dir=f"{ROOT_DIR}/providers/{args.provider}",
        variables={"api_token": args.api_token},
        terraform_bin_path=terr_path,
    )

    # make sure terraform is initialized
    ret, stdout, stderr = t.init()
    if ret != 0 and stderr:
        console.print("[red bold]Failed during initialization")
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)
        return
    
    current_workspace = get_current_workspace(t)

    # Is the current workspace different than the one we should be using?
    # listing is irrelevant for workspaces
    if (current_workspace != tf_workspace_name) and not args.list:
        workspaces = get_all_workspace(t)

        if tf_workspace_name not in workspaces:
            create_new_workspace(t, tf_workspace_name)
        else:
            select_workspace(t, tf_workspace_name)

    elif not (args.teardown or args.list):
        # Only 1 provider/region/image at a time
        console.print(f"[red bold]Provider/Region/Image Combination taken. Chose a different region, image, or provider.")
        return


    # now what do we want to do?
    if args.teardown:
        console.print(f"Tearing down {args.teardown}...", end="", style="bold italic")
        ret, stdout, stderr = t.cmd("apply", "-destroy", "-auto-approve",
                                var={
                                    "api_token": args.api_token,
                                    "image": args.image,
                                    "region": args.region
                                })
        if ret != 0 and stderr:
            stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
            print(stderr)

        # switch to default workspace
        ret, stdout, stderr = t.cmd("workspace", "select", "default")
        if ret != 0 and stderr:
            stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
            print(stderr)

        # delete old workspace
        ret, stdout, stderr = t.cmd("workspace", "delete", tf_workspace_name)
        if ret != 0 and stderr:
            stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
            print(stderr)

        rm_hosts(args.provider, tf_workspace_name)
        console.print("Done.")
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
                    ip = values['ip'] if 'ip' in values else 'UNK'
                    region = values['region'] if 'region' in values else 'UNK'
                    image = values['workspace'].split('_')[-1].replace('+', '/') if 'workspace' in values else 'UNK'
                    resources = values['resources'] if 'resources' in values else 'UNK'

                    table.add_row(hostname, ip, region, image, resources)
            console.print(table)
        return

    # prevent accidental creations
    if not args.setup:
        return

    # Creates new key pair
    if check_sshkeys(args.provider, args.region, args.image) is False:
        return

    # lets plan the config
    console.print("Preparing Configuration...", end="", style="bold italic")
    ret, stdout, stderr = t.cmd(
            "plan", f"-out={plan_path}", var={
                            "api_token": args.api_token, 
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
        return
    console.print("Done.")

    console.print("Configuring SSH Keys...", end="", style="bold italic")
    # Get Hostname and IP Adress
    output = t.output()

    new_hosts = dict()
    # digitalocean
    if "droplet_ip_address" in output:
        for hostname, ip_address in output["droplet_ip_address"]["value"].items():
            new_hosts[hostname] = {
                    'ip': ip_address, 
                    'region': args.region,
                    'resources': args.resources,
                    'workspace': tf_workspace_name
            }
            install_ssh_keys(args.provider, args.region, args.image, hostname, ip_address, args.user)

    # linode, aws
    elif "instance_ip_address" in output:
        for hostname, ip_address in output["instance_ip_address"]["value"].items():
            new_hosts[hostname] = {
                    'ip': ip_address, 
                    'region': args.region,
                    'resources': args.resources,
                    'workspace': tf_workspace_name
            }
            install_ssh_keys(args.provider, args.region, args.image, hostname, ip_address, args.user)

    # vultr
    elif "server_ip_address" in output:
        for hostname, ip_address in output["server_ip_address"]["value"].items():
            new_hosts[hostname] = {
                    'ip': ip_address, 
                    'region': args.region,
                    'resources': args.resources,
                    'workspace': tf_workspace_name
            }
            install_ssh_keys(args.provider, args.region, args.image, hostname, ip_address, args.user)
    console.print("Done.")

    save_hosts(args.provider, new_hosts)

    # Ansible configuration
    if args.custom:
        run_custom_playbook(args.custom, args.user)
    elif args.full:
        run_playbook('main.yml', args.user)
    elif args.minimal:
        run_playbook('minimal.yml', args.user)

    console.print("\nVPS' now available!\n", style="bold italic green")
    for host in new_hosts:
        console.print(f"ssh {host}", style="magenta")


if __name__ == "__main__":
    main()
