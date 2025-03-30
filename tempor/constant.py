#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from appdirs import user_config_dir, user_data_dir
import site
import os

provider_info = dict()

APP_NAME = "tempor"
APP_AUTHOR = "wh1t3fox"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = user_config_dir(APP_NAME)
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
BIN_DIR = site.getusersitepackages().split("lib")[0] + "bin"

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()
