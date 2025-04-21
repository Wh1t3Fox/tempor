#!/usr/bin/env python3
"""Import API classes."""

from .aws import AWS as aws
from .azure import Azure as azure
from .digitalocean import DigitalOcean as digitalocean
from .gcp import GCP as gcp
from .linode import Linode as linode
from .vultr import Vultr as vultr

# The names of the APIs need to be all lowercase
__all__ = ["aws", "azure", "digitalocean", "gcp", "linode", "vultr"]
