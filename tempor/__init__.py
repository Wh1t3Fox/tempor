#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Quick and Easy Infrastructure
"""

from appdirs import *
from pathlib import Path
import logging
import logging.config
import site
import sys
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "tempor"
APP_AUTHOR = "wh1t3fox"

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()

CONFIG_DIR = user_config_dir(APP_NAME)
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)

# this should drop bins in the same path as tempor
#BIN_DIR = os.path.dirname(sys.executable)
BIN_DIR = site.getusersitepackages().split('lib')[0] + 'bin'

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

provider_info = dict()
