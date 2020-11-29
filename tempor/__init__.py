#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path
import coloredlogs
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

coloredlogs.install()
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "loggers": {"": {"level": "DEBUG", "handlers": ["console", "file"]}},
        "formatters": {
            "colored_console": {
                "()": "coloredlogs.ColoredFormatter",
                "format": "%(levelname)s %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "file_format": {
                "format": "%(asctime)s :: %(funcName)s in %(filename)s (l:%(lineno)d) :: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "colored_console",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "level": "DEBUG",
                "formatter": "file_format",
                "class": "logging.FileHandler",
                "filename": f"{DATA_DIR}/tempor.log",
            },
        },
    }
)
logging.addLevelName(logging.DEBUG, "[+]")
logging.addLevelName(logging.INFO, "[i]")
logging.addLevelName(logging.WARNING, "[!]")
logging.addLevelName(logging.ERROR, "[-]")
