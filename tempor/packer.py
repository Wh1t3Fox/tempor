#!/usr/bin/env python3
"""Packer Class."""

from urllib.request import urlopen
from zipfile import ZipFile
from os import access, R_OK
from os.path import isfile
from io import BytesIO
import logging
import hashlib
import stat
import os

from .constants import (
    BIN_DIR,
    PACKER_VER,
    PACKER_ZIP_HASH,
    PACKER_FILE_HASH,
)
from .utils import (
    get_arch
)

class Packer:
    """Handler for Packer functionality."""

    def __init__(self, packer_fpath: str, var: dict = {}):
        self.logger = logging.getLogger(__name__)
        self.packer_fpath = packer_fpath
        self.var = var

        assert isfile(self.packer_fpath) and access(
            self.packer_fpath, R_OK
        ), f"File {self.packer_fpath} doesn't exist or isn't readable"

        if not self.is_installed():
            self.install_latest()

    def get_packer_path(self) -> str:
        """Return the full file path of the Packer executable.

        This is in the same dir as tempor, and this way it will not
        mess with any user installed terraform binaries.
        """
        return f"{BIN_DIR}/packer"

    def is_installed(self) -> bool:
        """Check if Packer is installed and Updated."""
        tf_path = self.get_packer_path()
        if arch := get_arch():
            if os.path.isfile(tf_path):
                with open(tf_path, "rb") as fr:
                    tf = BytesIO(fr.read())
                    if PACKER_FILE_HASH[arch] != hashlib.sha256(tf.getvalue()).hexdigest(): #noqa
                        return False
                    return True
            else:
                return False
        else:
            return False

    def install_latest(self) -> None:
        """Install latest version of Packer."""
        if not (arch := get_arch()):
            return

        url = f"https://releases.hashicorp.com/packer/{PACKER_VER}/packer_{PACKER_VER}_{arch}.zip"

        out_file = self.get_packer_path()
        self.logger.debug(f"Installing v{PACKER_VER}...")

        with urlopen(url) as zipresp:
            zipfile = BytesIO(zipresp.read())

            self.logger.debug(f"Validating Hash: {PACKER_ZIP_HASH[arch]}")
            assert (
                PACKER_ZIP_HASH[arch] == hashlib.sha256(zipfile.getvalue()).hexdigest()
            ), "Invalid SHA256 Hash of Zip File!"
            self.logger.debug("Passed!")
            with ZipFile(zipfile) as zfile:
                zfile.extractall(BIN_DIR)
            st = os.stat(out_file)
            os.chmod(out_file, st.st_mode | stat.S_IXUSR)

    def run_cmd(self, cmd: str) -> str:
        """Execute command and return reults."""
        return ""

    def init(self):
        """Packer init.

        Install missing plugins or upgrade plugins
        """
        pass

    def build(self):
        """Packer build.

        build image(s) from template
        """
        pass

    def validate(self):
        """Packer validate.

        check that a template is valid
        """
        pass

    def version(self) -> str:
        """Packer version."""
        return PACKER_VER

    def get_image_id(self):
        """Return the image id built from Packer."""
        pass
