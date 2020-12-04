#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from appdirs import *
from pathlib import Path
import logging
import logging.config
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "tempor"
APP_AUTHOR = "wh1t3fox"


CONFIG_DIR = user_config_dir(APP_NAME)
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)


BIN_DIR = f'{os.environ["HOME"]}/.local/bin'

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
