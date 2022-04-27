#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import shutil
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join("tempor", "VERSION"), "r", encoding="utf-8") as f:
    version = f.read()

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tempor",
    version=version,
    description="Ephemeral VPS Creation",
    license="GPT3",
    long_description=long_description,
    author="Wh1t3Fox",
    author_email="dev@exploit.design",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: Android",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    keywords=["VPS"],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    package_data={"tempor": ["config", "providers", "playbooks"]},
    install_requires=[
        "ansible==5.6.0",
        "appdirs==1.4.4",
        "ansible_runner==1.4.6",
        "jsonschema==3.2.0",
        "python-terraform==0.10.1",
        "rich==9.3.0",
        "ssh-config==0.0.22",
        "PyYAML==5.4.1",
        "boto3==1.22.1",
        "requests==2.27.1",
        "google-api-python-client==2.46.0"
    ],
    extras_require={
        "dev": [
            "black==20.8b1",
            "twine==3.2.0",
            "pytest==6.1.2",
            "pytest_cov==2.10.1",
            "flit==3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tempor = tempor.__main__:main",
        ],
    },
    include_package_data=True,
)
