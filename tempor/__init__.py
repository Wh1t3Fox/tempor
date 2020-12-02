#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path
import logging
import logging.config
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    CONFIG_DIR = f'{os.environ["XDG_CONFIG_HOME"]}/tempor'
except KeyError:
    CONFIG_DIR = f'{os.environ["HOME"]}/.config/tempor'

try:
    DATA_DIR = f"{os.environ['XDG_DATA_HOME']}/tempor"
except KeyError:
    DATA_DIR = f"{os.environ['HOME']}/.local/share/tempor"

BIN_DIR = f'{os.environ["HOME"]}/.local/bin'

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
