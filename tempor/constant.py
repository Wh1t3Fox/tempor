#!/usr/bin/env python3
"""Constants defined here."""

from appdirs import user_config_dir, user_data_dir
from os.path import expanduser
import site
import os

provider_info = {}

APP_NAME = "tempor"
APP_AUTHOR = "wh1t3fox"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = user_config_dir(APP_NAME)
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
BIN_DIR = site.getusersitepackages().split("lib")[0] + "bin"
SSH_CONFIG_PATH = expanduser("~/.ssh/config")

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()


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
