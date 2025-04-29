#!/usr/bin/env python3
"""Ansible playbook execution."""

from pathlib import Path
import ansible_runner
import logging
import shutil
import os

from .constants import ANSIBLE_HOSTS

def run_playbook(playbook: str,
                 user: str = "root") -> None:
    """Execute playbooks bundled with tempor."""
    logger = logging.getLogger(__name__)

    path = Path(playbook)
    parent_dir = path.parent.absolute()
    playbook = os.path.join(parent_dir, path.name)

    # copy our inventory file to the ansible dir
    try:
        shutil.copy(ANSIBLE_HOSTS, parent_dir)
    except FileNotFoundError:
        logger.error(f'{ANSIBLE_HOSTS} not found')
        return
    except PermissionError:
        logger.error(f'Permission to access {parent_dir}')
        return
    except Exception as e:
        logger.error(e)
        return

    ansible_runner.run(
        private_data_dir=parent_dir,
        playbook=playbook,
        verbosity=1,
        extravars={"ansible_user": user},
    )
