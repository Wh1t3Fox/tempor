#!/usr/bin/env python3
"""Constants defined here."""

from appdirs import user_config_dir, user_data_dir
from os.path import expanduser
import site
import sys
import os

provider_info = {}

APP_NAME = "tempor"
APP_AUTHOR = "wh1t3fox"

SSH_CONFIG_PATH = expanduser("~/.ssh/config")
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = user_config_dir(APP_NAME)
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)

HOSTS_FILE = f"{DATA_DIR}/hosts"
ANSIBLE_HOSTS = f"{ROOT_DIR}/playbooks/inventory"

# if we are in a virtualenv place it with the binaries
if os.environ.get('VIRTUAL_ENV') is not None:
    BIN_DIR = f"{sys.prefix}/bin"
else:
    # $HOME/.local/bin -- add to path if it's not (some dumb OS')
    BIN_DIR = site.getusersitepackages().split("lib")[0] + "bin"
    env_paths = os.environ.get("PATH", "").split(os.pathsep)

    # add to path -- only shows up for self and child processes
    if BIN_DIR not in env_paths:
        os.environ["PATH"] += os.pathsep + BIN_DIR


if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(BIN_DIR):
    os.makedirs(BIN_DIR)

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()

TF_VER = "1.11.4"
TF_ZIP_HASH = {
    "linux_amd64": "1ce994251c00281d6845f0f268637ba50c0005657eb3cf096b92f753b42ef4dc",
    "linux_386": "8e4bd232ce8b0cde2a90132a9c4d25665791c7a48bbb159f5cd4988265d10372",
    "linux_arm": "3cf072a049ab0178e9cbec47a14712ba7f38cc8ef061f3a7c0ff57b83d320edd",
    "linux_arm64": "a43d1d0da9b9bab214a8305a39db0e40869572594ccf50c416a7756499143633",
    "darwin_amd64": "a56d5002b9f7647291faccc3dd1a70350e60fb61e4c45037629508b8fdc2575b",
    "darwin_arm64": "867e0808fa971217043e25b7a792b10720c79b1546f8a68479b74f138be73e18"
}
TF_FILE_HASH = {
    "linux_amd64": "268000fca5c61021c6396893d9483007ba589ad9d0aaccbd7dfa8c78bf7dbe23",
    "linux_386": "37e8b85685b447593868a8f16d12e2678b3c1bc6212ca4dfefbf85402a6ffb7f",
    "linux_arm": "efc715a98ccb6ca961ccf591f28a8dd33f009e8f7821e1a6834b60fdd7ae002d",
    "linux_arm64": "377f01172f4a267672e0d0284c5c5589d477cba2f53b21e44e4bda30027d25b9",
    "darwin_amd64": "4ffae9d5e9429aa0c3ee96053eaea6770f1fe1886cc508f3c70e54c629aa4245",
    "darwin_arm64": "a451c0fbbb7cd5004e9aadf9ba6e2f5083a4530da99da1a460ee176ee9308c47",
}
