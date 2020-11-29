#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import shutil
import os

here = os.path.abspath(os.path.dirname(__file__))
version = '0.0.1'

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tempor',
    version=version,
    description='Ephemeral VPS Creation',
    license="GPT3",
    long_description=long_description,
    author='Wh1t3Fox',
    author_email='dev@exploit.design',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='ssh',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'colorama==0.4.3',
        'coloredlogs==14.0',
        'jsonschema==3.2.0',
        'prompt_toolkit==3.0.8', 
        'python-terraform==0.10.1', 
        'ssh-config==0.0.22',
        'PyYAML==5.3.1'
    ],
    entry_points={
        'console_scripts': [
            'tempor = tempor.__main__:main',
        ],
    },
    include_package_data=True,
)
