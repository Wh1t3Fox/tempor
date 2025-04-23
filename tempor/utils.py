#!/usr/bin/env python3
"""Utility helper functions."""

from rich.table import Table
from rich.console import Console
from rich.text import Text
from pathlib import Path
import jsonschema
import platform
import logging
import random
import string
import shutil
import json
import yaml
import os

from .constants import (
    ANSIBLE_HOSTS,
    CONFIG_DIR,
    HOSTS_FILE,
    provider_info,
    ROOT_DIR,
)
from .ssh import remove_config_entry

logger = logging.getLogger(__name__)

def log_table(rich_table):
    """Generate an ascii formatted presentation of a Rich table.

    Eliminates any column styling
    """
    console = Console()
    with console.capture() as capture:
        console.print(rich_table)
    return Text.from_ansi(capture.get())


def image_region_choices(provider: str) -> None:
    """Print information for `--aditional-info` arg."""
    if provider is None:
        return

    reg_table = Table(title="Regions")
    reg_table.add_column("ID", style="cyan")
    if provider == "gcp":
        reg_table.add_column("Zones", style="magenta")
    else:
        reg_table.add_column("Location", style="magenta")

    for _id, name in provider_info.get(provider, {}).get("regions", {}).items():
        reg_table.add_row(str(_id), str(name))

    img_table = Table(title="Images x86-64")
    img_table.add_column("ID", style="cyan")
    img_table.add_column("Name", style="magenta")
    for _id, name in provider_info.get(provider, {}).get("images", {}).items():
        img_table.add_row(str(_id), str(name))

    res_table = Table(title="Hardware Resources")
    res_table.add_column("ID", style="cyan")
    res_table.add_column("Price", style="magenta")
    res_table.add_column("Description", style="magenta")
    for k, v in provider_info.get(provider, {}).get("resources", {}).items():
        res_table.add_row(str(k), str(v["price"]), str(v["description"]))

    logger.info(log_table(reg_table))
    logger.info(log_table(img_table))
    logger.info(log_table(res_table))


def get_config() -> dict:
    """Parse config file."""
    fpath = f"{CONFIG_DIR}/config.yml"

    if not os.path.exists(fpath):
        logger.info(f"Creating New Config File: {fpath}")
        shutil.copy(f"{ROOT_DIR}/config/config.yml", fpath)
        return {}

    with open(fpath) as fr, open(f"{ROOT_DIR}/config/schema.yml") as fr2:
        try:
            cfg = yaml.safe_load(fr)
            schema = yaml.safe_load(fr2)
            jsonschema.validate(cfg, schema)
        except jsonschema.ValidationError as e:
            logger.error(f"[red bold]Invalid Config File: {fpath}[/]")
            if "api_token" in str(e):
                logger.error(
                    "[red bold]All Values are required. "
                            "Remove Providers without an API Token[/]"
                )
            else:
                logger.error(f"[red bold]{e}[/]")
            return {}
        return cfg


def rm_hosts(provider: str, vps_name: str = "") -> None:
    """Remove SSH Host entry."""
    hostnames = []
    hosts = get_hosts()

    if not hosts or (provider not in hosts):
        return

    for idx, host in enumerate(hosts[provider]):
        for hostname, _ in host.items():
            if vps_name:
                if hostname == vps_name:
                    hostnames.append(hostname)
                    del hosts[provider][idx]
                    remove_config_entry(hostname)
            else:
                hostnames.append(hostname)
                del hosts[provider][idx]
                remove_config_entry(hostname)

    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    if os.path.exists(ANSIBLE_HOSTS):
        with open(ANSIBLE_HOSTS) as fr, open(ANSIBLE_HOSTS, "w+") as fw:
            for line in fr:
                for hostname in hostnames:
                    line = line.replace(hostname, "")
                fw.write(line)


def get_hosts() -> dict:
    """Get all available hosts."""
    hosts = {}
    try:
        if os.path.exists(HOSTS_FILE):
            with open(HOSTS_FILE) as fr:
                hosts = json.load(fr)
    except json.decoder.JSONDecodeError:
        pass
    return hosts


def get_all_hostnames() -> list:
    """Get a list of all hostnames."""
    hostnames = []
    for _, servers in get_hosts().items():
        for vps in servers:
            for hostname in vps.keys():
                hostnames.append(hostname)
    return hostnames


def find_hostname(name: str) -> dict:
    """Return information on a hostname."""
    all_hosts = get_hosts()

    for provider in all_hosts:
        for idx, vps in enumerate(all_hosts[provider]):
            if name in vps:
                return all_hosts[provider][idx][name]
    return {}


def save_hosts(provider: str, new_hosts: dict) -> None:
    """Save host to file."""
    hosts = {}

    if not isinstance(new_hosts, dict):
        logger.error("[red bold]Cannot save new hosts[/]")
        return

    # load in what's there
    hosts = get_hosts()

    # combine 2 dictionaries
    if provider not in hosts:
        hosts[provider] = []

    hosts[provider].append(new_hosts)

    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    with open(ANSIBLE_HOSTS, "a+") as fw:
        for host in hosts[provider]:
            for hostname, _ in host.items():
                fw.write(f"{hostname}\n")

def get_arch() -> str:
    """Get system architecture."""
    uname = platform.uname()
    if "linux" in uname.system.lower():
        if "aarch64" in uname.machine:
            arch = "linux_arm64"
        elif "arm64" in uname.machine:
            arch = "linux_arm64"
        elif "64" in uname.machine:
            arch = "linux_amd64"
        elif "386" in uname.machine:
            arch = "linux_386"
        else:
            arch = "linux_arm"
    elif "darwin" in uname.system.lower():
        if "x86_64" in uname.machine:
            arch = "darwin_amd64"
        elif "aarch64" in uname.machine:
            arch = "darwin_arm64"
        elif "arm64" in uname.machine:
            arch = "darwin_arm64"
        else:
            arch = ""
    else:
        return ""
    return arch


def random_line(f: Path) -> str:
    """Return random line from file."""
    with open(f) as fr:
        lines = fr.read().splitlines()
        return random.choice(lines).replace("'", "").lower()


def random_number(min_val: int = 0, max_val: int = 100) -> str:
    """Generate a random number."""
    return str(random.randint(min_val, max_val))


def random_str(min_val: int = 5, max_val: int = 10) -> str:
    """Generate a random string."""
    return "".join(
        [
            random.choice(string.ascii_lowercase)
            for _ in range(random.randint(min_val, max_val))
        ]
    )


def random_name() -> str:
    """Return a random name for hostname."""
    try:
        wordlist = Path("/usr/share/dict/american-english")
        if not wordlist.is_file():
            raise FileNotFoundError
        return f"{random_line(wordlist)}{random_number()}"
    except FileNotFoundError:
        return f"{random_str()}{random_number()}"
