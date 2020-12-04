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


TER_VER = "0.13.5"
TER_HASH = {
    "amd64": "f7b7a7b1bfbf5d78151cfe3d1d463140b5fd6a354e71a7de2b5644e652ca5147",
    "386": "e497be04adfd5f03737ef0da5f705c5bac91a7178ba8786eef7e182c4883908b",
    "arm": "602e055078fa6be51983a58c6685fd48ee4dca9150c657da65604e9b8bfceced",
    "arm64": "e00d6140d3c92d337835ec968bf47233606943b9ce51467c5119ce8cfd97cc62",
    "darwin": "03f7b636638c587c3b03a4b3d1d4cab77c872ad5f7e55405ddaf38dfb94e0e89",
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
            console.print("[red bold]Invalid Config File")
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
    if not out_file:
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
