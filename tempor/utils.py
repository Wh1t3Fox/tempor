#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from typing import Dict
from rich.table import Table
from pathlib import Path
import jsonschema
import platform
import hashlib
import random
import string
import shutil
import json
import yaml
import stat
import os

from .constant import provider_info, ROOT_DIR, CONFIG_DIR, BIN_DIR, DATA_DIR
from .ssh import remove_config_entry
from .console import console

TF_VER = "1.11.3"
TF_ZIP_HASH = {
    "amd64": "377c8c18e2beab24f721994859236e98383350bf767921436511370d1f7c472b",
    "386": "f5a4250f371df3b9b54b7f802495a9e341a8846e3536f673d1f8c1d28e8c0b85",
    "arm": "9bf99463a9353a4242a5650fedc20833537db26c0aa7063ab673a179a5a7ba26",
    "arm64": "d685953bec501c0acda13319f34dddaadf33a8f553c85533531d3c7d5f84604a",
    "darwin": "bcdbb6f35c536da333d410cd0d0c1f5d543c4f40d46c8f96e419190fe3e9d941",
}
TF_FILE_HASH = {
    "amd64": "e42d3d36350c2fb085c9d6c8cb9e19bc3e86c1a295862731dad3a3d674a74f9c",
    "386": "fb8619837748bae100b65944c067a12f9e7f15ee04c729fd8f5c9103675c234c",
    "arm": "6c87a3200e3c58d4a804db31219756ae4cb47d221b4316c1825d71e11e26dc2f",
    "arm64": "c9652d71628df086d486c6d07609aae2f08a00c62cfb27a605a490ff71c19581",
    "darwin": "551e00959094b15424596a8786ad278c7b257c43c534cb1c5f2d2565ab142583",
}

HOSTS_FILE = f"{DATA_DIR}/hosts"
ANSIBLE_HOSTS = f"{ROOT_DIR}/playbooks/inventory"


def image_region_choices(provider: str) -> None:
    if provider is None:
        return

    reg_table = Table(title="Regions")
    reg_table.add_column("ID", style="cyan")
    if provider == "gcp":
        reg_table.add_column("Zones", style="magenta")
    else:
        reg_table.add_column("Location", style="magenta")

    for _id, name in provider_info[provider]["regions"].items():
        reg_table.add_row(str(_id), str(name))

    img_table = Table(title="Images x86-64")
    img_table.add_column("ID", style="cyan")
    img_table.add_column("Name", style="magenta")
    for _id, name in provider_info[provider]["images"].items():
        img_table.add_row(str(_id), str(name))

    res_table = Table(title="Hardware Resources")
    res_table.add_column("ID", style="cyan")
    res_table.add_column("Price", style="magenta")
    res_table.add_column("Description", style="magenta")
    for k, v in provider_info[provider]["resources"].items():
        res_table.add_row(str(k), str(v["price"]), str(v["description"]))

    print(
        f"""
usage: tempor {provider} [-h] [--image image] [--region region] [-s] [-l] [-b] [-m]

options:
  -h, --help            show this help message and exit
  -c, --count           Number of images to create
  --image image         Specify the OS Image
  --region region       Specify the Region to Host the Image
  --resources resource  Specify the hardware resources for the host image
  -l, --list            List Available VPS'
  -s, --setup           Create a VPS
  -f, --full            Full Configuration with hardening
  -m, --minimal         Minimal Configuration (just configs)
  --no-config           No Anisble setup at all
  -t, --tags            Add tags to aws EC2 instance
  --custom              Specify Ansible playbook for custom configuration (Path to main.yml file)
"""
    )
    console.print(reg_table)
    console.print(img_table)
    console.print(res_table)


def get_config() -> Dict:
    fpath = f"{CONFIG_DIR}/config.yml"

    if not os.path.exists(fpath):
        console.print(f"Creating New Config File: {fpath}")
        shutil.copy(f"{ROOT_DIR}/config/config.yml", fpath)
        return dict()

    with open(fpath) as fr, open(f"{ROOT_DIR}/config/schema.yml") as fr2:
        try:
            cfg = yaml.safe_load(fr)
            schema = yaml.safe_load(fr2)
            jsonschema.validate(cfg, schema)
        except jsonschema.exceptions.ValidationError as e:
            console.print(f"[red bold]Invalid Config File: {fpath}")
            if "api_token" in str(e):
                console.print(
                    "[red bold]All Values are required. Remove Providers without an API Token"
                )
            else:
                console.print(f"[red bold]{e}")
            return dict()
        return cfg


def terraform_installed() -> str:
    updated = True
    out_file = shutil.which("terraform")

    uname = platform.uname()
    if "linux" in uname.system.lower():
        if "aarch64" in uname.machine:
            arch = "arm64"
        elif "64" in uname.machine:
            arch = "amd64"
        elif "386" in uname.machine:
            arch = "386"
        else:
            arch = "arm"
        url = f"https://releases.hashicorp.com/terraform/{TF_VER}/terraform_{TF_VER}_linux_{arch}.zip"
    elif "darwin" in uname.system.lower():
        arch = "darwin"
        url = f"https://releases.hashicorp.com/terraform/{TF_VER}/terraform_{TF_VER}_darwin_amd64.zip"
    else:
        return ""

    # Check if we've already installed
    if not out_file:
        out_file = f"{BIN_DIR}/terraform"
    else:  # check version
        with open(out_file, "rb") as fr:
            tf = BytesIO(fr.read())

            if TF_FILE_HASH[arch] != hashlib.sha256(tf.getvalue()).hexdigest():
                updated = False

    if not os.path.exists(out_file) or not updated:
        out_file = f"{BIN_DIR}/terraform"
        console.print(
            f"Terraform not in Path or Out-of-Date. Installing v{TF_VER} to {out_file} ..."
        )

        with urlopen(url) as zipresp:
            zipfile = BytesIO(zipresp.read())

            console.print(f"Validating Hash: {TF_ZIP_HASH[arch]}")
            assert (
                TF_ZIP_HASH[arch] == hashlib.sha256(zipfile.getvalue()).hexdigest()
            ), "Invalid SHA256 Hash of Zip File!"
            console.print("Passed!")
            with ZipFile(zipfile) as zfile:
                zfile.extractall(f"{BIN_DIR}")
            st = os.stat(out_file)
            os.chmod(out_file, st.st_mode | stat.S_IXUSR)
    return out_file


def rm_hosts(provider: str, vps_name: str = "") -> None:
    hostnames = list()
    hosts = get_hosts()

    if not hosts or (provider not in hosts):
        return

    for idx, host in enumerate(hosts[provider]):
        for hostname, values in host.items():
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


def get_hosts() -> Dict:
    hosts = dict()
    try:
        if os.path.exists(HOSTS_FILE):
            with open(HOSTS_FILE) as fr:
                hosts = json.load(fr)
    except json.decoder.JSONDecodeError:
        pass
    return hosts


def find_hostname(name: str) -> str:
    all_hosts = get_hosts()

    for provider in all_hosts:
        for idx, vps in enumerate(all_hosts[provider]):
            if name in vps:
                return all_hosts[provider][idx][name]
    return ""


"""
{
    '<provider>': [
        '<hostname>': {
            'ip': '<ip>',
            'workspace': '<workspace>'
        },
    ]
}
"""


def save_hosts(provider: str, new_hosts: dict) -> None:
    hosts = dict()

    if not isinstance(new_hosts, dict):
        console.print("[red bold]Cannot save new hosts")
        return

    # load in what's there
    hosts = get_hosts()

    # combine 2 dictionaries
    if provider not in hosts:
        hosts[provider] = list()

    hosts[provider].append(new_hosts)

    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    with open(ANSIBLE_HOSTS, "a+") as fw:
        for host in hosts[provider]:
            for hostname, values in host.items():
                fw.write(f"{hostname}\n")


def random_line(f: str) -> str:
    with open(f) as fr:
        lines = fr.read().splitlines()
        return random.choice(lines).replace("'", "").lower()


def random_number(min_val: int = 0, max_val: int = 100) -> str:
    return str(random.randint(min_val, max_val))


def random_str(min_val: int = 5, max_val: int = 10) -> str:
    return "".join(
        [
            random.choice(string.ascii_lowercase)
            for _ in range(random.randint(min_val, max_val))
        ]
    )


def random_name() -> str:
    try:
        wordlist = Path("/usr/share/dict/american-english")
        if not wordlist.is_file():
            raise FileNotFoundError
        return f"{random_line(wordlist)}{random_number()}"
    except FileNotFoundError:
        return f"{random_str()}{random_number()}"
