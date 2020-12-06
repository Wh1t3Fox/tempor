#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
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

from tempor import ROOT_DIR, CONFIG_DIR, BIN_DIR, DATA_DIR
from tempor.console import console
from tempor.ssh import remove_config_entry


TER_VER = "0.14.0"
TER_HASH = {
    "amd64": "07fd7173f7a360ad5e4d5ea5035670cf426cf7a08d0486bc0fe7c9d76b447722",
    "386": "40c78d378bfabb3f3905440ab3d49d4bd718634fbaea3ab58772af89905569a9",
    "arm": "57e5b3e312b7f75c04b0071c1d39ed4de58c71e1e47e7bdf7ef9ad5be7041246",
    "arm64": "290c437ab37a1f54717daaef359f4935a1fdcdf036bc43fca25e8565c00262d7",
    "darwin": "e728f9c5f64b9a7507f7038ad243743b4bcad0057fe7cc83021eb825cc2b6b9c",
}

HOSTS_FILE = f"{DATA_DIR}/hosts"
ANSIBLE_HOSTS = f"{ROOT_DIR}/playbooks/inventory"


def get_config():
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


def terraform_installed():
    out_file = shutil.which("terraform")

    # Check if we've already installed
    if not out_file:
        out_file = f"{BIN_DIR}/terraform"

    if not os.path.exists(out_file):
        out_file = f"{BIN_DIR}/terraform"
        console.print(f"Terraform not in Path. Installing to {out_file} ...")
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
            url = f"https://releases.hashicorp.com/terraform/{TER_VER}/terraform_{TER_VER}_linux_{arch}.zip"
        elif "darwin" in uname.system.lower():
            arch = "darwin"
            url = f"https://releases.hashicorp.com/terraform/{TER_VER}/terraform_{TER_VER}_darwin_amd64.zip"
        else:
            return None

        h = hashlib.sha256()
        with urlopen(url) as zipresp:
            zipfile = BytesIO(zipresp.read())

            console.print(f"Validating Hash: {TER_HASH[arch]}")
            assert (
                TER_HASH[arch] == hashlib.sha256(zipfile.getvalue()).hexdigest()
            ), "Invalid SHA256 Hash of Zip File!"
            console.print("Passed!")
            with ZipFile(zipfile) as zfile:
                zfile.extractall(f"{BIN_DIR}")
            st = os.stat(out_file)
            os.chmod(out_file, st.st_mode | stat.S_IXUSR)
    return out_file


def rm_hosts(provider):
    hosts = get_hosts()

    if not hosts or provider not in hosts:
        return

    for hostname in hosts[provider]:
        remove_config_entry(hostname)

    del hosts[provider]

    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    if os.path.exists(ANSIBLE_HOSTS):
        with open(ANSIBLE_HOSTS, "w+") as fw:
            fw.write("")


def get_hosts():
    hosts = dict()
    try:
        if os.path.exists(HOSTS_FILE):
            with open(HOSTS_FILE) as fr:
                hosts = json.load(fr)
    except json.decoder.JSONDecodeError:
        pass
    return hosts


def save_hosts(provider, new_hosts):
    hosts = dict()

    if not isinstance(new_hosts, dict):
        console.print("[red bold]Cannot save new hosts")
        return

    # load in what's there
    try:
        if os.path.exists(HOSTS_FILE):
            with open(HOSTS_FILE) as fr:
                hosts = json.load(fr)
    except json.decoder.JSONDecodeError:
        pass  # Invalid file so lets overwrite it

    # combine 2 dictionaries
    if provider not in hosts:
        hosts[provider] = dict()

    hosts[provider].update(new_hosts)

    with open(HOSTS_FILE, "w") as fw:
        json.dump(hosts, fw)

    with open(ANSIBLE_HOSTS, "a+") as fw:
        for host, ip in hosts[provider].items():
            fw.write(f"{host}\n")


def random_line(f):
    with open(f) as fr:
        lines = fr.read().splitlines()
        return random.choice(lines).replace("'", "").lower()


def random_number(min_val=0, max_val=100):
    return str(random.randint(min_val, max_val))


def random_str(min_val=5, max_val=10):
    return "".join(
        [
            random.choice(string.ascii_lowercase)
            for _ in range(random.randint(min_val, max_val))
        ]
    )


def random_name():
    try:
        wordlist = Path("/usr/share/dict/american-english")
        if not wordlist.is_file():
            raise FileNotFoundError
        return f"{random_line(wordlist)}{random_number()}"
    except FileNotFoundError:
        return f"{random_str()}{random_number()}"
