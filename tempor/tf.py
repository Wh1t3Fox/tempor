#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import Terraform
from pathlib import Path
import sys
import re
import os

from .constant import ROOT_DIR
from .console import console
from .workspaces import (
    get_current_workspace,
    get_all_workspace,
    create_new_workspace,
    select_workspace
)
from .utils import terraform_installed, rm_hosts


class TF:
    def __init__(self, provider, region, image, api_token=None, tags=dict()):
        self.provider = provider
        self.region = region
        self.image = image
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
        if provider == 'aws' and self.api_token:
            os.environ['AWS_ACCESS_KEY_ID'] = self.api_token['access_key']
            os.environ['AWS_SECRET_ACCESS_KEY'] = self.api_token['secret_key']
            os.environ['AWS_REGION'] = self.region
        elif provider == 'aws' and not self.api_token:
            if not (os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_SECRET_ACCESS_KEY')):
                console.print('[red]No AWS API Tokens detected.[/red]')
                sys.exit(1)

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


    def get_output(self) -> str:
        return self.t.output()


    def get_plan_path(self) -> str:
        plan_path =  f"{ROOT_DIR}/providers/{self.provider}/files/plans/{self.region}/{self.image}/plan"

        # Create dirs if needed
        plan_parent_path = Path(plan_path).parent.absolute()
        if not os.path.exists(plan_parent_path):
            os.makedirs(plan_parent_path)

        return plan_path


    def get_active_workspace(self) -> str:
        return get_current_workspace(self.t)


    def get_workspace_name(self) -> str:
        # The name must contain only URL safe characters, and no path separators.
        return f"{self.provider}_{self.region}_{self.image}".replace("/", "+")


    def correct_workspace(self) -> bool:
        return self.get_active_workspace() == self.workspace_name


    def setup_workspace(self) -> None:
        # Is the current workspace different than the one we should be using?
        # listing is irrelevant for workspaces
        if self.get_active_workspace() != self.workspace_name:
            workspaces = get_all_workspace(self.t)

            if self.workspace_name not in workspaces:
                create_new_workspace(self.t, self.workspace_name)
            else:
                select_workspace(self.t, self.workspace_name)


    def plan(self, count = 1) -> bool:
        ret, stdout, stderr = self.t.cmd(
            "plan",
            f"-out={self.get_plan_path()}",
            var={
                "api_token": self.api_token,
                "image": self.image,
                "region": self.region,
                "num": count,
                "tags": self.tags
            },
        )
        if ret != 0 and stderr:
            # Fix the color escape sequences
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
            return False
        return True


    def apply(self) -> bool:
        ret, stdout, stderr = self.t.cmd("apply", self.get_plan_path())
        if ret != 0 and stderr:
            # Fix the color escape sequences
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
            return False
        return True


    def teardown(self, hostname: str) ->  None:
        '''
        If therer are more than 1, remove just this instance, else remove everything
        '''

        ret, stdout, stderr = self.t.cmd("show")
        if ret != 0 and stderr:
            stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
            print(stderr)
        output = self.t.output()

        if "droplet_ip_address" in output:
            num_instances = len(output["droplet_ip_address"]["value"])
        elif "instance_ip_address" in output:
            num_instances = len(output["instance_ip_address"]["value"])
        elif "server_ip_address" in output:
            num_instances = len(output["server_ip_address"]["value"])
        else:
            num_instances = 0

        if num_instances > 1:
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
                    "tags": self.tags
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


