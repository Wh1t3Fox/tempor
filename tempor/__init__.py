#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Quick and Easy Infrastructure
"""
import os

from . import playbook, ssh, tf, utils, workspaces
__all__ = ['playbook', 'ssh', 'tf', 'utils', 'workspaces']

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fr:
    __version__ = fr.read().strip()
