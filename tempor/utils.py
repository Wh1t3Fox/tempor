#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# TODO: Call the provider APIs instead of this stupid hard coding

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
