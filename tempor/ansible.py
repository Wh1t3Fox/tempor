#!/usr/bin/env python3
"""Ansible playbook execution."""

from pathlib import Path
import ansible_runner
import os

def run_playbook(playbook: str,
                 user: str = "root") -> None:
    """Execute playbooks bundled with tempor."""
    path = Path(playbook)
    parent_dir = path.parent.absolute()
    playbook = os.path.join(parent_dir, path.name)

    ansible_runner.run(
        private_data_dir=parent_dir,
        playbook=playbook,
        verbosity=1,
        extravars={"ansible_user": user},
    )
