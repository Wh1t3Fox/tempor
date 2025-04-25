#!/usr/bin/env python3
"""SSH Handler Functions."""

from os import path
import ssh_config
import subprocess
import logging
import shutil
import os

from .constants import ROOT_DIR, DATA_DIR, SSH_CONFIG_PATH

logger = logging.getLogger(__name__)

def add_config_entry(hostname: str, attr: dict) -> None:
    """Add entry to SSH config."""
    new_host = ssh_config.Host(hostname, attr)

    # does ~/.ssh/config exist?
    if not path.isfile(SSH_CONFIG_PATH):
        # ~/.ssh/ ?
        if not path.exists(os.path.dirname(SSH_CONFIG_PATH)):
            os.makedirs(os.path.dirname(SSH_CONFIG_PATH))
        # create ~/.ssh/config
        cfg = ssh_config.SSHConfig.create(SSH_CONFIG_PATH)
    else:
        cfg = ssh_config.SSHConfig(SSH_CONFIG_PATH)

    try:
        cfg.add(new_host)
    except ssh_config.errors.HostExistsError:  #pyright: ignore
        cfg.update(hostname, attr)
    cfg.write()


def remove_config_entry(hostname: str) -> None:
    """Remove entry from SSH config."""
    # Nothing to remove if config doesn't exist
    if not path.isfile(SSH_CONFIG_PATH):
        return

    cfg = ssh_config.SSHConfig(SSH_CONFIG_PATH)

    try:
        cfg.remove(hostname)
        cfg.write()
    except (KeyError, NameError):
        pass

    try:
        shutil.rmtree(f"{DATA_DIR}/{hostname}")
    except OSError:
        pass

    try:
        shutil.rmtree(f"{ROOT_DIR}/playbooks/artifacts")
    except OSError:
        pass


def check_sshkeys(provider: str, region: str, image: str, hostname: str) -> bool:
    """Check if key exists, and create it if not."""
    # azure only allows RSA keys, so dumb
    key_type = "rsa" if provider == "azure" else "ed25519"

    prog = shutil.which("ssh-keygen")
    if not prog:
        logger.info("[red bold]ssh-keygen not available. Is OpenSSH installed?[/]")
        return False

    out_dir = f"{ROOT_DIR}/providers/{provider}/files/{region}/{image}/{hostname}/.ssh"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_file = f"{out_dir}/id_{key_type}"
    if not os.path.exists(out_file):
        logger.info("[bold italic]Generating new key pair...[/]")
        subprocess.call(
            f'yes | ssh-keygen -t {key_type} -N "" -C "" -f {out_file}',
            stdout=subprocess.DEVNULL,
            shell=True,
        )
    return True


def install_ssh_keys(
    provider: str, region: str, image: str, hostname: str, ip_address: str, user: str
) -> None:
    """Install SSH config to correct dir."""
    old_dir = f"{ROOT_DIR}/providers/{provider}/files/{region}/{image}/{hostname}/.ssh"
    out_dir = f"{DATA_DIR}/{hostname}/ssh"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for fname in os.listdir(old_dir):
        shutil.copy(os.path.join(old_dir, fname), out_dir)

    attr = {
        "Hostname": ip_address,
        "User": user,
        "Port": 22,
        "Compression": "yes",
        "StrictHostKeyChecking": "no",
        "UserKnownHostsFile": "/dev/null",
        "IdentityFile": f"{out_dir}/id_ed25519",
        "IdentityAgent": "none",
        "IdentitiesOnly": "yes",
    }
    add_config_entry(hostname, attr)
