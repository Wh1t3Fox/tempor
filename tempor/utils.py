#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from typing import Dict, List
from rich.table import Table
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

from tempor import provider_info, ROOT_DIR, CONFIG_DIR, BIN_DIR, DATA_DIR
from tempor.console import console
from tempor.ssh import remove_config_entry

TF_VER = "1.1.9"
TF_ZIP_HASH = {
    "amd64": "9d2d8a89f5cc8bc1c06cb6f34ce76ec4b99184b07eb776f8b39183b513d7798a",
    "386": "a29a5c069e1712753ed553f7c6e63f1cd35caefee73496210461c05158b836b4",
    "arm": "800eee18651b5e552772c60fc1b5eb00cdcefddf11969412203c6de6189aa10a",
    "arm64": "e8a09d1fe5a68ed75e5fabe26c609ad12a7e459002dea6543f1084993b87a266",
    "darwin": "c902b3c12042ac1d950637c2dd72ff19139519658f69290b310f1a5924586286",
}
TF_FILE_HASH = {
    "amd64": "8d5b3b0a164e95de9cafbdd6ca16a1ec439927b9bb6ec146b9566473ca796cc0",
    "386": "db94691af978caa67b2c6a527d46cf8c7ea738c42a3750a121ddf4eb993bab25",
    "arm": "4c797f48f7614706e35ecd60e16f0c776404515119d37eed44c0417194a0426b",
    "arm64": "d501a25b7f95dfa3d5414bc4fc5382c09fe926464c4114a288ddbd7bb688d94c",
    "darwin": "41ea760fa6b4b60525731af0acda64e76cc21f098a6f33b7c92868f5c8667a7f",
}

HOSTS_FILE = f"{DATA_DIR}/hosts"
ANSIBLE_HOSTS = f"{ROOT_DIR}/playbooks/inventory"


def image_region_choices(provider: str) -> str:
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


def get_config() -> Dict:
    fpath = f"{CONFIG_DIR}/config.yml"

    if not os.path.exists(fpath):
        console.print(f"Creating New Config File: {fpath}")
        shutil.copy(f"{ROOT_DIR}/config/config.yml", fpath)
        return None

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
            return None
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
        return None

    # Check if we've already installed
    if not out_file:
        out_file = f"{BIN_DIR}/terraform"
    else:  # check version
        h = hashlib.sha256()
        with open(out_file, 'rb') as fr:
            tf = BytesIO(fr.read())

            if TF_FILE_HASH[arch] != hashlib.sha256(tf.getvalue()).hexdigest():
                updated = False


    if not os.path.exists(out_file) or not updated:
        out_file = f"{BIN_DIR}/terraform"
        console.print(f"Terraform not in Path or Out-of-Date. Installing v{TF_VER} to {out_file} ...")

        h = hashlib.sha256()
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


def rm_hosts(provider: str, workspace: str) -> None:
    hostnames = list()
    hosts = get_hosts()

    if not hosts or provider not in hosts:
        return

    for idx, host in enumerate(hosts[provider]):
        for hostname, values in host.items():
            if values['workspace'] == workspace:
                hostnames.append(hostname)
                del hosts[provider][idx]
                remove_config_entry(hostname)


    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    if os.path.exists(ANSIBLE_HOSTS):
        with open(ANSIBLE_HOSTS) as fr, open(ANSIBLE_HOSTS, "w+") as fw:
            for line in fr:
                for hostname in hostnames:
                    line = line.replace(hostname, '')
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


'''
{
    '<provider>': [
        '<hostname>': {
            'ip': '<ip>',
            'workspace': '<workspace>'
        },
    ]
}
'''
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


def random_number(min_val: int = 0, max_val: int = 100) -> int:
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
