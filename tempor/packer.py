#!/usr/bin/env python3
"""Packer Class."""

from urllib.request import urlopen
from zipfile import ZipFile
from os import access, R_OK
from os.path import isfile
from io import BytesIO
import subprocess
import logging
import hashlib
import shlex
import stat
import sys
import os

from .exceptions import (
    PackerConfigurationError,
    AuthorizationError,
    UnsupportedProviderError
)
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

    def __init__(self, provider: str, packer_fpath: str,
                 region: str, resources: str, api_token=None
    ):
        self.logger = logging.getLogger(__name__)
        self.packer_img_id = ''

        self.provider = provider
        self.packer_fpath = packer_fpath
        self.region = region
        self.resources = resources
        self.api_token = api_token

        assert isfile(self.packer_fpath) and access(
            self.packer_fpath, R_OK
        ), f"File '{self.packer_fpath}' doesn't exist or isn't readable"

        if not self.is_installed():
            self.install_latest()

        if provider == 'aws':
            self.api_token = {} if self.api_token is None else self.api_token

            # if the API tokens in the config are populated set them to env variables
            if (
                self.api_token.get("access_key", None) is not None
                and self.api_token.get("secret_key", None) is not None
            ):
                os.environ["AWS_ACCESS_KEY_ID"] = self.api_token["access_key"]
                os.environ["AWS_SECRET_ACCESS_KEY"] = self.api_token["secret_key"]

            # Do we have env vars being passed!?,
            # assume the use is competent and setup all the envs
            elif os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get(
                "AWS_SECRET_ACCESS_KEY"
            ):
                pass # don't need to do anything :)

            # do we only have a profile specified?
            elif profile := self.api_token.get("profile", None):
                pass # don't have to do anything here either :)

            else:
                self.logger.error("[red]No AWS API Tokens detected.[/red]")
                sys.exit(1)

            # does the user want to run as a different profile?
            if profile := self.api_token.get("profile", None):
                os.environ["AWS_PROFILE"] = profile

            # just make sure our region is set
            if os.environ.get("AWS_REGION", None) is None:
                os.environ["AWS_REGION"] = self.region
        elif provider == 'digitalocean':
            if self.api_token is not None:
                os.environ['DIGITALOCEAN_ACCESS_TOKEN'] = self.api_token
            else:
                raise AuthorizationError('No API Token Specified')
        elif provider == 'linode':
            if self.api_token is not None:
                os.environ['LINODE_TOKEN'] = self.api_token
            else:
                raise AuthorizationError('No API Token Specified')
        else:
            raise UnsupportedProviderError


    def get_packer_path(self) -> str:
        """Return the full file path of the Packer executable.

        This is in the same dir as tempor, and this way it will not
        mess with any user installed packer binaries.
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

    def run_cmd(self, cmd: str) -> tuple[str, str]:
        """Execute command and return reults."""
        args = shlex.split(cmd)
        res =  subprocess.run(args, capture_output=True, text=True)
        return (res.stdout, res.stderr)

    def init(self):
        """Packer init.

        Install missing plugins or upgrade plugins
        """
        self.logger.info('[bold italic]Installing missing plugins...[/]')
        stdout, stderr = self.run_cmd(
                    f'{self.get_packer_path()}'
                    ' init '
                    f'{os.path.dirname(self.packer_fpath)}'
                )
        if stderr:
            self.logger.error(stderr)

        if 'Error' in stdout:
            self.logger.error(stdout)
            raise PackerConfigurationError

        return (stdout, stderr)

    def build(self):
        """Packer build.

        build image(s) from template
        """
        self.logger.info('[bold italic]Building image...[/]')
        stdout, stderr = self.run_cmd(
                    f'{self.get_packer_path()}'
                    ' build '
                    f'{self.get_variables()}'
                    f'{os.path.dirname(self.packer_fpath)}'
                )
        if stderr:
            self.logger.error(stderr)

        match stdout:
            case stdout if 'Error' in stdout:
                self.logger.error(stdout)
                raise PackerConfigurationError
            case stdout if 'status code: 401' in stdout:
                raise AuthorizationError
            case stdout if 'InvalidGrantException' in stdout:
                raise AuthorizationError
            case _:
                self.packer_img_id = stdout.split('\n')[-3].split(':')[-1].strip()

        if self.packer_img_id:
            self.logger.info(f'[blue]Created image {self.packer_img_id}[/]')

    def fmt(self):
        """Packer fmt.

        Format template
        """
        stdout, stderr = self.run_cmd(
                    f'{self.get_packer_path()}'
                    ' fmt '
                    f'{os.path.dirname(self.packer_fpath)}'
                    f'{self.get_variables()}'
                )
        if stderr:
            self.logger.error(stderr)

        if 'Error' in stdout:
            self.logger.error(stdout)
            raise PackerConfigurationError

    def validate(self):
        """Packer validate.

        check that a template is valid
        """
        self.logger.info('[bold italic]Validating file...[/]')
        stdout, stderr = self.run_cmd(
                    f'{self.get_packer_path()}'
                    ' validate '
                    f'{os.path.dirname(self.packer_fpath)}'
                    f'{self.get_variables()}'
                )
        if stderr:
            self.logger.error(stderr)

        if 'Error' in stdout:
            self.logger.error(stdout)
            raise PackerConfigurationError

        return (stdout, stderr)

    def is_valid(self) -> bool:
        """Check if Packer config is valid."""
        stdout, stderr = self.validate()
        if stderr:
            return False
        return True

    def get_variables(self) -> str:
        """Get variables being passed to the config."""
        variables = (
            f'-var region={self.region} '
            f'-var resources={self.resources} '
        )
        return variables

    def get_image_id(self) -> str:
        """Return the image id built from Packer."""
        return self.packer_img_id

    def get_ssh_user(self) -> str:
        """Return the username for SSH."""
        username = ''
        with open(self.packer_fpath) as fr:
            # ['ssh_username = "ubuntu"']
            users = [line.strip().split('=')[1].translate(str.maketrans("","",' "')) \
                    for line in fr.readlines() if 'ssh_username' in line]
            users = list(set(users)) # remove dups
            # this can be more than 1, not sure what to do then
            # maybe just return them all with the image_id (image_id, username)
            if users:
                username = users[0]
        return username
