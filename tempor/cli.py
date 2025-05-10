#!/usr/bin/env python3
"""Main CLI interface."""

from rich.prompt import Confirm
from rich.table import Table
from os import access, R_OK
from os.path import isfile
import subprocess
import argparse
import logging
import json
import sys

from tempor.constants import pkg_version, provider_info
from tempor.exceptions import UnsupportedProviderError
from tempor.ssh import check_sshkeys, install_ssh_keys
from tempor.ansible import run_playbook
from tempor.utils import (
    find_hostname,
    get_all_hostnames,
    get_config,
    get_hosts,
    image_region_choices,
    save_hosts,
    log_table
)
from tempor.terraform import Terraform
from tempor.packer import Packer
from tempor.apis import * # noqa

logger = logging.getLogger(__name__)

def print_subparser_help(parser: argparse.ArgumentParser, provider: str) -> None:
    """Find the correct subparser to print help."""
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]

    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == provider:
                subparser.print_help()
                break


def get_args() -> argparse.Namespace:
    """Parse cli arguments and setup env."""
    cfg = get_config()

    if not cfg:
        sys.exit(1)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-t",
        "--teardown",
        default=None,
        choices=get_all_hostnames(),
        help="Name of VPS Image to Tear down",
    )
    parser.add_argument("-u", "--update", action="store_true", help="Check for Upates")
    parser.add_argument("--version", action="store_true", help="Print current version")

    # build args for each provider
    subparsers = parser.add_subparsers(dest="provider")
    for entry in cfg.get("providers", []):
        provider = entry.get("name")
        if provider == "aws":
            api_token = entry.get("api_token", {})
        else:
            api_token = entry.get("api_token", "")

        provider_info[provider] = {}
        provider_info[provider]["api_token"] = api_token

        prov_parser = subparsers.add_parser(provider, add_help=False)
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
            "--hostname",
            metavar="hostname",
            help="Specify the name of the VPS",
        )
        if provider == "aws":
            prov_parser.add_argument(
                "--cidr-block",
                metavar="cidr_block",
                default="10.253.0.0/16",
                help="IPv4 CIDR block for VPC",
            )
            prov_parser.add_argument(
                "-p",
                "--profile",
                metavar="profile",
                help="AWS profile to use for authentication",
            )
            prov_parser.add_argument(
                "-t",
                "--tags",
                type=json.loads,
                default="{}",
                metavar="tags",
                help="Tags to add to the instance",
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
            "--ansible",
            metavar="ansible",
            type=str,
            help="Specify Ansible playbook for custom configuration "
                    "(Path to main.yml file)",
        )
        prov_parser.add_argument(
            "--packer",
            metavar="packer",
            type=str,
            help="Specify Packer config for custom configuration "
                    "(Path to *.pkr.hcl file)",
        )
        prov_parser.add_argument(
            "--additional-info",
            action="store_true",
            help="Displays available regions, images, and resources (with --help)",
        )

    args = parser.parse_args()

    if args.version:
        logger.info(pkg_version)
        sys.exit(0)

    elif args.update:
        logger.info("Checking for updates...")
        res = subprocess.check_output(
            ["python3", "-m", "pip", "list", "--outdated", "--not-required"],
            stderr=subprocess.DEVNULL,
        ).decode()

        if parser.prog in res:
            offset = res.find(parser.prog)
            res = res[offset:]
            _name, _, c_ver, _, _, l_ver, _ = res.split(" ", 6)
            logger.info(f"[green]Version {l_ver} available!")
            if choice := Confirm.ask("Would you like to update? (Y/n)"):
                try:
                    assert choice
                    subprocess.check_output(
                        ["python3", "-m", "pip", "install", "-U", "tempor"],
                        stderr=subprocess.DEVNULL,
                    )
                except AssertionError:
                    pass
        else:
            logger.info("Running latest version.")
        sys.exit(0)

    elif args.teardown:
        return args

    # check options for this provider
    for p in cfg.get("providers", {}):
        if p.get("name") == args.provider:

            if image := p.get("image"):
                if not args.image:
                    args.image = image

            # GCP only
            if zone := p.get("zone"):
                if not args.zone:
                    args.zone = zone

            if region := p.get("region"):
                if not args.region:
                    args.region = region

            if resources := p.get("resources"):
                if not args.resources:
                    args.resources = resources

            if api_token := p.get("api_token"):
                args.api_token = api_token

            try:
                # AWS specific
                if args.profile is not None:
                    if args.api_token is None:
                        args.api_token = {}
                    args.api_token["profile"] = args.profile
            except AttributeError:
                pass

            break
    else:
        parser.print_help()
        sys.exit(1)

    # don't need API auth to print normal help
    if args.additional_info is False and args.help is True:
        print_subparser_help(parser, args.provider)
        parser.exit(0)

    # check for files access
    if args.packer is not None:
        assert isfile(args.packer) and access(
            args.packer, R_OK
        ), f"File '{args.packer}' doesn't exist or isn't readable"

    if args.ansible is not None:
        assert isfile(args.ansible) and access(
            args.ansible, R_OK
        ), f"File '{args.ansible}' doesn't exist or isn't readable"

    API = globals()[args.provider](api_token, args.region)
    # validate API creds
    if not API.is_authorized():
        logger.info(
                f"[red bold] Invalid {args.provider} API Token."
        )
        sys.exit(1)

    # check for null values in args
    if args.list is False and (args.region is None or \
            args.resources is None or \
            args.image is None):
        raise Exception('Missing arguments. Region, Image, and Resources are required!')


    if args.provider == "gcp":
        # make sure the image/region combo is allowed
        valid_zone = API.valid_zone(args.zone)
        try:
            assert valid_zone
        except AssertionError:
            logger.info(f"[red]{args.zone} is not valid[/red]")
            sys.exit(1)
        args.region = args.zone

    provider_info[args.provider]["regions"] = API.get_regions()
    provider_info[args.provider]["images"] = API.get_images(args.region)
    provider_info[args.provider]["resources"] = API.get_resources(args.region)

    if args.region not in provider_info.get(args.provider, {}).get("regions", []):
        logger.info(f"[red bold]{args.region} is not a supported region")
        print_subparser_help(parser, args.provider)
        image_region_choices(args.provider)
        parser.exit(0)

    args.user = globals()[args.provider].get_user(args.image, args.region)

    # this needs to come after populating the info above
    if args.additional_info is True and args.help is True:
        print_subparser_help(parser, args.provider)
        image_region_choices(args.provider)
        parser.exit(0)


    # make sure the image/region combo is allowed
    try:
        assert API.valid_image_in_region(args.image, args.region)
    except AssertionError:
        logger.info(f"[red]{args.image} is not available in {args.region}[/red]")
        sys.exit(1)

    # make sure the CPU RAM resources are allowed in this region
    try:
        assert API.valid_resource_in_region(args.resources, args.region)
    except AssertionError:
        logger.info(f"[red]{args.resources} is not available in {args.region}[/red]")
        sys.exit(1)

    return args


def main(args = None, override_teardown: bool = False) -> None:
    """Start Program."""
    if not args:
        args = get_args()

    # if teardown we need to look up some info
    if args.teardown:
        args.list = False
        _host = find_hostname(args.teardown)

        if not _host:
            logger.info(f"[red bold]{args.teardown} is not a valid hostname")
            return None

        _provider, _, _image, _ = (
            _host.get("workspace", "").replace("+", "/").split("_")
        )
        args.provider = _provider
        args.region = _host.get("region", "")
        args.image = _image
        args.resources = _host.get("resources", "")
        args.api_token = provider_info.get(args.provider, {}).get("api_token", "")
        args.hostname = args.teardown

    # need to build our image for Terraform
    if hasattr(args, 'packer') and args.packer is not None:
        if args.provider not in ['aws', 'digitalocean', 'linode']:
            raise UnsupportedProviderError

        p = Packer(
            args.provider,
            args.packer,
            args.region,
            args.resources,
            args.api_token
        )
        p.init()
        p.validate()
        p.build()
        args.image = p.get_image_id()
        if ssh_username := p.get_ssh_user():
            args.user = ssh_username

    tf = Terraform(
        args.provider,
        args.region,
        args.image,
        args.resources,
        args.hostname,
        args.api_token,
        tags = args.tags if hasattr(args, 'tags') else None,
        cidr_block = args.cidr_block if hasattr(args, 'cidr_block') else None
    )
    tf_workspace_name = tf.get_workspace_name()

    if override_teardown:
        args.teardown = tf_workspace_name
        args.setup = False

    # make sure we have the correct workspace, and create it if it does not exist
    if not tf.correct_workspace() and not args.list:
        tf.setup_workspace()
    elif not (args.teardown or args.list):
        # Only 1 provider/region/image at a time
        logger.info(
            "[red bold]Provider/Region/Image/Hostname Combination taken. "
                    "Chose a different provider, region, image, or hostname."
        )
        return

    # now what do we want to do?
    if args.teardown:
        logger.info(f"[bold italic]Tearing down {args.teardown}...[/]")
        tf.teardown(args.teardown)
        exit()

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
                    ip = values.get("ip", "UNK")
                    region = values.get("region", "UNK")
                    try:
                        image = (
                            values.get("workspace", "UNK")
                            .split("_")[-2]
                            .replace("+", "/")
                        )
                    except IndexError:
                        image = "UNK"
                    resources = values.get("resources", "UNK")

                    table.add_row(hostname, ip, region, image, resources)
            logger.info(log_table(table))
        return

    # prevent accidental creations
    if not args.setup:
        logger.info("[red]Specify -s/--setup to create an instance.[/red]")
        return

    logger.info("[bold italic]Configuring SSH Keys...[/]")
    # Creates new key pair
    if (
        check_sshkeys(args.provider, args.region, args.image, tf.get_vps_name())
        is False
    ):
        return

    # lets plan the config
    logger.info("[bold italic]Preparing Configuration...[/]")
    if not tf.plan(args.count):
        # if plan fails -- teardown
        main(args, True)

    # now apply the config
    logger.info("[bold italic]Creating VPS...[/]")
    if not tf.apply():
        # if apply fails -- teardown
        main(args, True)

    hostname = ""
    for hostname, val in tf.get_new_hosts().items():
        install_ssh_keys(
            args.provider,
            val.get("region"),
            val.get("image"),
            hostname,
            val.get("ip"),
            args.user,
        )
        save_hosts(args.provider, {hostname: val})

    if args.ansible:
        run_playbook(args.ansible, args.user)

    if hostname:
        logger.info(f"[bold italic green]VPS {hostname} now available![/]")


if __name__ == "__main__":
    main()
