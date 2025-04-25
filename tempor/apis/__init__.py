#!/usr/bin/env python3
"""Import API classes."""

from tempor.apis.aws import AWS as aws
from tempor.apis.azure import Azure as azure
from tempor.apis.digitalocean import DigitalOcean as digitalocean
from tempor.apis.gcp import GCP as gcp
from tempor.apis.linode import Linode as linode
from tempor.apis.vultr import Vultr as vultr

# The names of the APIs need to be all lowercase
__all__ = ["aws", "azure", "digitalocean", "gcp", "linode", "vultr"]
