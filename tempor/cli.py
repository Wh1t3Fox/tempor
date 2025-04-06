#!/usr/bin/env python3
"""Main CLI interface."""

from rich.prompt import Confirm
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
    get_all_hostnames,
    get_config,
    get_hosts,
    image_region_choices,
    save_hosts,
)
from .tf import TF
from .apis import * # noqa


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
    providers_failed_auth = []
    for entry in cfg.get("providers", []):
        provider = entry.get("name")
        if provider == "aws":
            api_token = entry.get("api_token", {})
        else:
            api_token = entry.get("api_token", "")

        provider_info[provider] = {}
        provider_info[provider]["api_token"] = api_token

        # validate API creds
        if not getattr(globals()[provider], "authorized")(api_token):
            providers_failed_auth.append(provider)

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
            default=True,
            help="Do not run any configuration (except custom)",
        )
        prov_parser.add_argument(
            "--custom",
            type=str,
            default=False,
            help="Specify Ansible playbook for custom configuration "
                    "(Path to main.yml file)",
        )
        prov_parser.add_argument(
            "--additional-info",
            action="store_true",
            help="Displays available regions, images, and resources (with --help)",
        )

    args = parser.parse_args()

    if providers_failed_auth:
        for provider in providers_failed_auth:
            console.print(
                f"[red bold] Invalid {provider} API Token. Fix or remove provider."
            )
        sys.exit(1)

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
            console.print("Running latest version.")
        sys.exit(0)

    elif args.teardown:
        return args

    # This is default behavior
    if args.setup and not (args.minimal or args.full or args.custom):
        # update args based upon config
        if config := cfg.get("config"):
            # first set is mutually exclusive, but custom can be used with any
            if config.get("none") is True:
                args.no_config = True
                args.minimal = False
                args.full = False
            elif config.get("bare") is True:
                args.no_config = False
                args.minimal = False
                args.full = False
            elif config.get("minimal") is True:
                args.no_config = False
                args.minimal = True
                args.full = False
            elif config.get("full") is True:
                args.no_config = False
                args.minimal = False
                args.full = True

            if custom := config.get("custom"):
                args.minimal = False
                args.full = False
                args.custom = custom

    if args.custom:
        file = args.custom
        assert isfile(file) and access(
            file, R_OK
        ), f"File {file} doesn't exist or isn't readable"

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

                # AWS specific
                # override config with cli arg
                if api_token.get("profile") is None and \
                        args.profile is not None:
                            args.api_token["profile"] = args.profile
            break
    else:
        parser.print_help()
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
        try:
            assert valid_zone
        except AssertionError:
            console.print(f"[red]{args.zone} is not valid[/red]")
            sys.exit(1)

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

    if args.region not in provider_info.get(args.provider, {}).get("regions", []):
        console.print(f"[red bold]{args.region} is not a supported region")
        print_subparser_help(parser, args.provider)
        image_region_choices(args.provider)
        parser.exit(0)

    args.user = getattr(globals()[args.provider], "get_user")(args.image, args.region)

    # this needs to come after populating the info above
    if args.help:
        print_subparser_help(parser, args.provider)
        if args.additional_info:
            image_region_choices(args.provider)
        parser.exit(0)

    # make sure the image/region combo is allowed
    try:
        assert getattr(globals()[args.provider], "valid_image_in_region")(
            args.image, args.region, args.api_token
        )
    except AssertionError:
        console.print(f"[red]{args.image} is not available in {args.region}[/red]")
        sys.exit(1)

    # make sure the CPU RAM resources are allowed in this region
    try:
        assert getattr(globals()[args.provider], "valid_resource_in_region")(
            args.resources, args.region, args.api_token
        )
    except AssertionError:
        console.print(f"[red]{args.resources} is not available in {args.region}[/red]")
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
            console.print(f"[red bold]{args.teardown} is not a valid hostname")
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

    tf = TF(
        args.provider,
        args.region,
        args.image,
        args.resources,
        args.hostname,
        args.api_token,
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
        console.print(
            "[red bold]Provider/Region/Image/Hostname Combination taken. "
                    "Chose a different provider, region, image, or hostname."
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
            console.print(table)
        return

    # prevent accidental creations
    if not args.setup:
        console.print("[red]Specify -s/--setup to create an instance.[/red]")
        return

    console.print("Configuring SSH Keys...", end="", style="bold italic")
    # Creates new key pair
    if (
        check_sshkeys(args.provider, args.region, args.image, tf.get_vps_name())
        is False
    ):
        return
    console.print("Done.")

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

    if hostname:
        console.print(f"\nVPS {hostname} now available!\n", style="bold italic green")


if __name__ == "__main__":
    main()
