#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssh_config
from ssh_config import SSHConfig, Host
from os.path import expanduser
from pathlib import Path
from os import path
import subprocess
import logging
import shutil
import shlex
import sys
import os

from tempor import ROOT_DIR, DATA_DIR

logger = logging.getLogger(__name__)

SSH_CONFIG_PATH = expanduser('~/.ssh/config')

def add_config_entry(hostname, attr):
    new_host = Host(hostname, attr)

    # does ~/.ssh/config exist?
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        # ~/.ssh/ ? 
        if not path.exists(os.path.dirname(SSH_CONFIG_PATH)):
            os.makedirs(os.path.dirname(SSH_CONFIG_PATH))
        # create ~/.ssh/config
        cfg = SSHConfig(expanduser(SSH_CONFIG_PATH))
        cfg.append(new_host)
        cfg.write()
    else:
        cfg = SSHConfig.load(expanduser(SSH_CONFIG_PATH))
        cfg.append(new_host)

def remove_config_entry(hostname):
    # Nothing to remove if config doesn't exist
    if not path.isfile(expanduser(SSH_CONFIG_PATH)):
        return

    cfg = SSHConfig.load(expanduser(SSH_CONFIG_PATH))

    try:
        cfg.remove(hostname)
    except KeyError:
        pass

def check_sshkeys(provider):
    prog = shutil.which('ssh-keygen')
    if not prog:
        logger.errror('ssh-keygen not available. Is OpenSSH installed?')
        return False

    out_dir = f'{ROOT_DIR}/providers/{provider}/files/.ssh'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_file = f'{out_dir}/id_ed25519'
    if not os.path.exists(out_file):
        sys.stdout.write('[i] Generating new key pair...')
        subprocess.call(f'yes | ssh-keygen -t ed25519 -N "" -C "" -f {out_file}', stdout=subprocess.DEVNULL, shell=True)
        sys.stdout.write('Done.\n')

def install_ssh_keys(provider, hostname, ip_address):
    old_dir = f'{ROOT_DIR}/providers/{provider}/files/.ssh'
    out_dir = f'{DATA_DIR}/{hostname}/ssh'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for fname in os.listdir(old_dir):
        shutil.copy(os.path.join(old_dir, fname), out_dir)

    attr = {
        'Hostname': ip_address,
        'User': 'root',
        'Port': 22,
        'Compression': True,
        'StrictHostKeyChecking': 'no',
        'IdentityFile': f'{out_dir}/id_ed25519'
    }
    add_config_entry(hostname, attr)
