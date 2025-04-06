#!/usr/bin/env python3
"""Terraform Class."""

from python_terraform import Terraform
from pathlib import Path
import sys
import re
import os

from .constant import ROOT_DIR
from .console import console
from .utils import terraform_installed, rm_hosts, random_line, random_number, random_str


class TF:
    """Handler for all of the Terraform functionality."""

    def __init__(
        self, provider, region, image, resources, vps_name=None, api_token=None, tags={}
    ):
        self.provider = provider
        self.region = region
        self.image = image
        self.resources = resources
        self.vps_name = self.generate_vps_name() if not vps_name else vps_name
        self.api_token = api_token
        self.tags = tags

        self.workspace_name = self.get_workspace_name()

        # check if terraform is installed
        terr_path = terraform_installed()
        if terr_path is None:
            console.print("[red bold]Platform not Supported")
            sys.exit(1)

        # pass tokens for AWS thourh ENV
        # this allows the user to also just set the ENV variables as well
        # ENV set here are only accessible to the child processes
        if self.provider == "aws":
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
                console.print("[red]No AWS API Tokens detected.[/red]")
                sys.exit(1)

            # does the user want to run as a different profile?
            if profile := self.api_token.get("profile", None):
                os.environ["AWS_PROFILE"] = profile

            # just make sure our region is set
            if os.environ.get("AWS_REGION", None) is None:
                os.environ["AWS_REGION"] = self.region


        # Create the Object
        self.t = Terraform(
            working_dir=f"{ROOT_DIR}/providers/{self.provider}",
            variables={"api_token": self.api_token},
            terraform_bin_path=terr_path,
        )

        # Initialize
        ret, stdout, stderr = self.t.init()
        if ret != 0 and stderr:
            console.print("[red bold]Failed during initialization")
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
            return

    def get_vps_name(self) -> str:
        """Return VPS name."""
        return self.vps_name

    def get_output(self) -> dict:
        """Return output from Terraform."""
        output =  self.t.output()
        if output is None:
            return {}
        return output

    def get_plan_path(self) -> str:
        """Return fullpath of the Terraform Plan."""
        plan_path = (f"{ROOT_DIR}/providers/{self.provider}/files/"
                     f"plans/{self.region}/{self.image}/{self.vps_name}/plan")

        # Create dirs if needed
        plan_parent_path = Path(plan_path).parent.absolute()
        if not os.path.exists(plan_parent_path):
            os.makedirs(plan_parent_path)

        return plan_path

    def get_active_workspace(self) -> str:
        """Return active workspace."""
        return self.get_current_workspace()

    def get_current_workspace(self) -> str:
        """Get the current workspace."""
        ret, stdout, stderr = self.t.cmd("workspace", "show")
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)

        if stdout:
            return stdout.strip()
        return ""

    def get_all_workspace(self) -> list[str]:
        """Get all the workspaces."""
        ret, stdout, stderr = self.t.cmd("workspace", "list")
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)

        if stdout:
            return [s.strip("* ").strip() for s in stdout.split("\n")]
        return []

    def create_new_workspace(self, name: str) -> bool:
        """Create a new workspace."""
        ret, stdout, stderr = self.t.cmd("workspace", "new", name)
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)

            return False

        return True

    def select_workspace(self, name: str) -> bool:
        """Change to the correct workspace."""
        ret, stdout, stderr = self.t.cmd("workspace", "select", name)
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)

            return False

        return True

    def get_workspace_name(self) -> str:
        """Return the name of the active workspace."""
        # The name must contain only URL safe characters, and no path separators.
        return f"{self.provider}_{self.region}_{self.image}_{self.vps_name}".replace(
            "/", "+"
        )

    def correct_workspace(self) -> bool:
        """Check if the active workspace is our current."""
        return self.get_active_workspace() == self.workspace_name

    def setup_workspace(self) -> None:
        """Setup/Configure new workspace."""
        # Is the current workspace different than the one we should be using?
        # listing is irrelevant for workspaces
        if self.get_active_workspace() != self.workspace_name:
            workspaces = self.get_all_workspace()

            if self.workspace_name not in workspaces:
                self.create_new_workspace(self.workspace_name)
            else:
                self.select_workspace(self.workspace_name)

    def get_new_hosts(self) -> dict:
        """Parse the Terraform setup and save the new hosts."""
        new_hosts = {}

        # figure out which provider we are
        output = self.get_output()
        for instance_type in [
                'droplet_ip_address',
                'instance_ip_address',
                'server_ip_address'
                ]:
            if instance := output.get(instance_type, None): # noqa
                for hostname, ip_address in (
                    instance.get("value").items()
                ):
                    new_hosts[hostname] = {
                        "ip": ip_address,
                        "region": self.region,
                        "image": self.image,
                        "resources": self.resources,
                        "workspace": self.get_workspace_name(),
                    }
        return new_hosts

    def plan(self, count=1) -> bool:
        """Terraform plan."""
        ret, stdout, stderr = self.t.cmd(
            "plan",
            f"-out={self.get_plan_path()}",
            var={
                "api_token": self.api_token,
                "image": self.image,
                "region": self.region,
                "resources": self.resources,
                "num": count,
                "vps_name": self.vps_name,
                "tags": self.tags,
            },
        )
        if ret != 0 and stderr:
            # Fix the color escape sequences
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
            return False
        return True

    def apply(self) -> bool:
        """Terraform apply."""
        ret, stdout, stderr = self.t.cmd("apply", self.get_plan_path())
        if ret != 0 and stderr:
            # Fix the color escape sequences
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
            return False
        return True

    def teardown(self, hostname: str) -> None:
        """If there are more than 1, remove just this instance.
        else remove everything."""
        ret, stdout, stderr = self.t.cmd("show")
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)

        output = self.get_output()
        for instance_type in [
                'droplet_ip_address',
                'instance_ip_address',
                'server_ip_address'
            ]:
            if instance := output.get(instance_type, None):
                num_instances = len(instance.get("value", []))
                break
        else:
            num_instances = 0

        if num_instances > 1 and stdout is not None:
            # find resources we want to teardown
            stdout = stdout[: stdout.find(hostname)]
            # search right to left for vps resource
            stdout = stdout[: stdout.rfind("vps")]
            # find the full resource name and index
            target = stdout[stdout.rfind("#") + 2 : stdout.rfind(":")]

            ret, stdout, stderr = self.t.cmd(
                "apply",
                "-destroy",
                "-auto-approve",
                f"-target={target}",
                var={
                    "api_token": self.api_token,
                    "image": self.image,
                    "region": self.region,
                    "resources": self.resources,
                    "vps_name": self.vps_name,
                    "tags": self.tags,
                },
            )
            if ret != 0 and stderr:
                stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
                print(stderr)
            rm_hosts(self.provider, hostname)
        else:
            # destroy all the resources (1 running instance)
            ret, stdout, stderr = self.t.cmd(
                "apply",
                "-destroy",
                "-auto-approve",
                var={
                    "api_token": self.api_token,
                    "image": self.image,
                    "region": self.region,
                    "resources": self.resources,
                    "vps_name": self.vps_name,
                    "tags": self.tags,
                },
            )
            if ret != 0 and stderr:
                stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
                print(stderr)

            # switch to default workspace
            ret, stdout, stderr = self.t.cmd("workspace", "select", "default")
            if ret != 0 and stderr:
                stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
                print(stderr)

            # delete old workspace
            ret, stdout, stderr = self.t.cmd("workspace", "delete", self.workspace_name)
            if ret != 0 and stderr:
                stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
                print(stderr)

            rm_hosts(self.provider)
        console.print("Done.")
        return

    def generate_vps_name(self) -> str:
        """Generate random VPS name."""
        try:
            wordlist = Path("/usr/share/dict/american-english")
            if not wordlist.is_file():
                raise FileNotFoundError
            name = f"{random_line(wordlist)}{random_number()}"
        except FileNotFoundError:
            name = f"{random_str()}{random_number()}"

        return name


