#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import jsonschema
import subprocess
import platform
import logging
import hashlib
import shutil
import shlex
import yaml
import stat
import os

from tempor import ROOT_DIR, CONFIG_DIR, BIN_DIR

logger = logging.getLogger(__name__)

TER_VER='0.13.5'
TER_HASH= {
    'amd64':'f7b7a7b1bfbf5d78151cfe3d1d463140b5fd6a354e71a7de2b5644e652ca5147',
    '386': 'e497be04adfd5f03737ef0da5f705c5bac91a7178ba8786eef7e182c4883908b'
}

def get_config():
    fpath = f'{CONFIG_DIR}/config.yml'

    if not os.path.exists(fpath):
        logger.info(f'Creating New Config File: {fpath}')
        shutil.copy(f'{ROOT_DIR}/config/config.yml', fpath)
        return None
    
    with open(fpath) as fr, open(f'{ROOT_DIR}/config/schema.yml') as fr2:
        try:
            cfg = yaml.safe_load(fr)
            schema = yaml.safe_load(fr2)
            jsonschema.validate(cfg, schema)
        except jsonschema.exceptions.ValidationError as e:
            logger.error(e)
            return None
        return cfg


def terraform_installed():
    out_file = shutil.which('terraform')
    if not out_file:
        out_file = f'{BIN_DIR}/terraform'
        logger.error(f'Terraform not in Path. Installing to {out_file} ...')
        uname = platform.uname()
        if 'linux' in uname.system.lower():
            if '64' in uname.machine:
                arch = 'amd64'
            else:
                arch = '386'
            url = f'https://releases.hashicorp.com/terraform/{TER_VER}/terraform_{TER_VER}_linux_{arch}.zip'
        else:
            return None

        h = hashlib.sha256()
        with urlopen(url) as zipresp:
            zipfile = BytesIO(zipresp.read())

            logger.info(f'Validating Hash: {TER_HASH[arch]}')
            assert TER_HASH[arch] == hashlib.sha256(zipfile.getvalue()).hexdigest(), "Invalid SHA256 Hash of Zip File!"
            logger.info('Passed!')
            with ZipFile(zipfile) as zfile:
                zfile.extractall(f'{BIN_DIR}')
            st = os.stat(out_file)
            os.chmod(out_file, st.st_mode | stat.S_IXUSR)
    return out_file

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
        logger.info(f'Generating new key pair {out_file}')
        subprocess.call(f'yes | ssh-keygen -t ed25519 -N "" -C "" -f {out_file}', stdout=subprocess.DEVNULL, shell=True)
