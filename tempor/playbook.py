#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ansible_runner
import os

from tempor import ROOT_DIR
from tempor.console import console


def run_playbook(playbook: str = "main.yml", user: str = "root") -> None:
    ansible_runner.run(
        private_data_dir=f"{ROOT_DIR}/playbooks", playbook=playbook, verbosity=1, 
        extravars = {"ansible_user": user}
    )
