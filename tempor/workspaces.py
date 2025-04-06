#!/usr/bin/env python3
"""Terraform workspace helper functions."""
import python_terraform
import re


def get_current_workspace(tf: python_terraform.Terraform) -> str:
    """Get the current workspace."""
    ret, stdout, stderr = tf.cmd("workspace", "show")
    if ret != 0 and stderr:
        stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
        print(stderr)

    if stdout:
        return stdout.strip()
    return ""


def get_all_workspace(tf: python_terraform.Terraform) -> list[str]:
    """Get all the workspaces."""
    ret, stdout, stderr = tf.cmd("workspace", "list")
    if ret != 0 and stderr:
        stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
        print(stderr)

    if stdout:
        return [s.strip("* ").strip() for s in stdout.split("\n")]
    return []


def create_new_workspace(tf: python_terraform.Terraform, name: str) -> bool:
    """Create a new workspace."""
    ret, stdout, stderr = tf.cmd("workspace", "new", name)
    if ret != 0 and stderr:
        stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
        print(stderr)

        return False

    return True


def select_workspace(tf: python_terraform.Terraform, name: str) -> bool:
    """Change to the correct workspace."""
    ret, stdout, stderr = tf.cmd("workspace", "select", name)
    if ret != 0 and stderr:
        stderr = re.sub(r"(\[\d+m)", r"\033\1", stderr)
        print(stderr)

        return False

    return True
