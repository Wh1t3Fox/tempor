#!/usr/bin/env python3
"""Linode API."""

import requests

from .api import API
from .helpers import authorized

class Linode(API):
    """Linode API Class."""

    API_URL = "https://api.linode.com/v4"

    def __init__(self, api_token: str, region: str = ''):
        super().__init__(api_token, region)

    def get_account(self) -> dict:
        """Get account information."""
        return requests.get(
            f"{Linode.API_URL}/account",
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        ).json()

    def is_authorized(self) -> bool:
        """Check if API token is valid."""
        try:
            resp = self.get_account()
        except Exception:
            return False

        if "errors" in resp:
            return False

        return True

    @authorized
    def get_images(self, region: str = "") -> dict:
        """Get available images."""
        images = {}

        page = 1
        while True:
            resp = requests.get(
                f"{Linode.API_URL}/images?page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()
            for image in resp["data"]:
                if image["status"] == "available":
                    images[image["id"]] = image["label"]

            if page == resp["pages"]:
                break
            page += 1

        return images

    @authorized
    def get_regions(self) -> dict:
        """Get available regions."""
        regions = {}

        page = 1
        while True:
            resp = requests.get(
                f"{Linode.API_URL}/regions?page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for region in resp["data"]:
                if "Linodes" in region["capabilities"]:
                    regions[region["id"]] = region["country"]

            if page == resp["pages"]:
                break
            page += 1

        return regions

    @authorized
    def get_resources(self, region: str = "") -> dict:
        """Get available resource types."""
        types = {}

        page = 1
        while True:
            resp = requests.get(
                f"{Linode.API_URL}/linode/types?page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for _type in resp["data"]:
                types[_type["id"]] = {
                    "description": _type["label"],
                    "price": f"${_type['price']['hourly']}/hr",
                }

            if page == resp["pages"]:
                break
            page += 1

        return types

    @authorized
    def valid_image_in_region(self, image: str, region: str) -> bool:
        """Linode does not restrict images in regions."""
        return True

    @authorized
    def valid_resource_in_region(self, resource: str, region: str) -> bool:
        """Linode does not restrict types in regions."""
        return True

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return SSH user."""
        return "root"
