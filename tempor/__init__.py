#!/usr/bin/env python3
"""Quick and Easy Infrastructure."""
import os

from . import playbook, ssh, tf, utils

__all__ = ["playbook", "ssh", "tf", "utils"]

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()
