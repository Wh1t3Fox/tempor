#!/usr/bin/env python3
"""Quick and Easy Infrastructure."""
import os

from . import ansible, ssh, terraform, utils

__all__ = ["ansible", "ssh", "terraform", "utils"]

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()
