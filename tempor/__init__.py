#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Quick and Easy Infrastructure
"""
import os

from . import playbook, ssh, utils, workspaces
__all__ = ['playbook', 'ssh', 'utils', 'workspaces']

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()
