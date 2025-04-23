#!/usr/bin/env python3
"""Ansible playbook execution."""

from pathlib import Path
import ansible_runner
import os

from .constants import ROOT_DIR


def run_playbook(playbook: str = "full.yml",
                 user: str = "root",
                 custom: bool = False) -> None:
    """Execute playbooks bundled with tempor."""
    if custom is True:
        path = Path(playbook)
        parent_dir = path.parent.absolute()
        playbook = os.path.join(parent_dir, path.name)
    else:
        parent_dir = f"{ROOT_DIR}/playbooks"

    ansible_runner.run(
        private_data_dir=parent_dir,
        playbook=playbook,
        verbosity=1,
        extravars={"ansible_user": user},
    )
