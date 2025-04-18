#!/usr/bin/env python3
"""Ansible playbook execution."""

from pathlib import Path
import ansible_runner
import os

from .constant import ROOT_DIR


def run_playbook(playbook: str = "full.yml", user: str = "root") -> None:
    """Execute playbooks bundled with tempor."""
    ansible_runner.run(
        private_data_dir=f"{ROOT_DIR}/playbooks",
        playbook=playbook,
        verbosity=1,
        extravars={"ansible_user": user},
    )


def run_custom_playbook(playbook, user: str = "root") -> None:
    """Execute playbook from the --custom argument."""
    # make sure we convert to full paths
    path = Path(playbook)
    parent_dir = path.parent.absolute()
    full_path = os.path.join(parent_dir, path.name)

    ansible_runner.run(
        private_data_dir=parent_dir,
        playbook=full_path,
        verbosity=1,
        extravars={"ansible_user": user},
    )
