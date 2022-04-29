#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Terraform workspace helper functions
'''
from typing import List
import python_terraform
import re


def get_current_workspace(tf: python_terraform.Terraform) -> str:
    ret, stdout, stderr = tf.cmd("workspace", "show")
    if ret != 0 and stderr:
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)

    return stdout.strip()


def get_all_workspace(tf: python_terraform.Terraform) -> List[str]:
    ret, stdout, stderr = tf.cmd("workspace", "list")
    if ret != 0 and stderr:
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)
    
    return list(map(lambda s: s.strip('* ').strip(), stdout.split('\n')))


def create_new_workspace(tf: python_terraform.Terraform, name: str) -> bool:
    ret, stdout, stderr = tf.cmd("workspace", "new", name)
    if ret != 0 and stderr:
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)

        return False

    return True


def select_workspace(tf: python_terraform.Terraform, name: str) -> bool:
    ret, stdout, stderr = tf.cmd("workspace", "select", name)
    if ret != 0 and stderr:
        stderr = re.sub(f'(\[\d+m)', r'\033\1', stderr)
        print(stderr)

        return False

    return True
