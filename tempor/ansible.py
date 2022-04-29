#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ansible_runner
import os

from tempor import ROOT_DIR, DATA_DIR
from tempor.console import console


def run_playbook(playbook: str = "main.yml") -> None:
    ansible_data = f"{DATA_DIR}/ansible"
    if not os.path.exists(ansible_data):
        os.makedirs(ansible_data)

    ansible_runner.run(
        private_data_dir=f"{ROOT_DIR}/playbooks", playbook=playbook, verbosity=5
    )
