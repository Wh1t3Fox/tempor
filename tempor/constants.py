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
ANSIBLE_HOSTS = f"{DATA_DIR}/inventory"

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
    pkg_version = fr.read().strip()

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

PACKER_VER = "1.12.0"
PACKER_ZIP_HASH = {
    "linux_amd64": "e859a76659570d1e29fa55396d5d908091bacacd4567c17770e616c4b58c9ace",
    "linux_386": "2fba1a4d61386805069416764da34bb7af1d48747530be570a9452b28f6d99fa",
    "linux_arm": "29c8cb058b6d0d68c84e4a322c4abb1b11bdfe926d9a16ccbf4e026b8df75e49",
    "linux_arm64": "a9ea40e7757cd000836b650bd2ed825dc3af9a7d73f4e19119df4c1aa13d0fe6",
    "darwin_amd64": "2cdaa91b640974ad65fa95b112f4604a9c272e38f7e9f9d853aa33774aa4feeb",
    "darwin_arm64": "448bebeb5741eebd5fdc92609e75213665366970cd607ec57e7a5516d7067b3d"
}
PACKER_FILE_HASH = {
    "linux_amd64": "dce0dab683b9f4bc447b53ebfa1fedf0f0620d702af66d8b0b36f9cc8ecf1369",
    "linux_386": "bf945d31731323f89fbc173317d30adcf9604bb25335153d2a6ca2ed46f23d71",
    "linux_arm": "bef1ca5d81eeaa1210af99875101107d0a529e3acd35015e776d64c0ee786227",
    "linux_arm64": "7a47088a35d87af5a6cd298b974971144dc1a3dca717c6a35aaa813940476997",
    "darwin_amd64": "254d6fb20679eb5aaa18dfcdfb35b980c3a399b7c4c241167da1bce8cdc63281",
    "darwin_arm64": "a2c3a143560c5f17b5d7c819f6d505ebaf87ba6faffcd30cbde43a6773a2112a",
}
