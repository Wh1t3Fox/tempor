#!/usr/bin/env python3
"""DigitalOcean API."""

import requests

from .api import API
from .helpers import authorized

class DigitalOcean(API):
    """DO API Class."""

    API_URL = "https://api.digitalocean.com/v2"

    def __init__(self, api_token: str, region: str = ''):
        super().__init__(api_token, region)

    def get_account(self) -> dict:
        """"Get account information."""
        return requests.get(
            f"{DigitalOcean.API_URL}/account",
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

        if resp.get("id") == "Unauthorized":
            return False

        return True

    @authorized
    def get_images(self, region: str = "") -> dict:
        """Get types of images."""
        images = {}

        page = 1
        while True:
            resp = requests.get(
                f"{DigitalOcean.API_URL}/images?per_page=500&page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for image in resp["images"]:
                images[image["slug"]] = image["name"]

            if not resp["links"] or "last" not in resp["links"]["pages"]:
                break

            page += 1

        return images

    @authorized
    def get_regions(self) -> dict:
        """Get possible regions."""
        regions = {}

        page = 1
        while True:
            resp = requests.get(
                f"{DigitalOcean.API_URL}/regions?per_page=500&page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for region in resp["regions"]:
                if region["available"] is True:
                    regions[region["slug"]] = region["name"]

            if not resp["links"] or "last" not in resp["links"]["pages"]:
                break

            page += 1

        return regions

    @authorized
    def get_resources(self, region: str = "") -> dict:
        """Get possible resource types."""
        sizes = {}

        page = 1
        while True:
            resp = requests.get(
                f"{DigitalOcean.API_URL}/sizes?per_page=500&page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for size in resp["sizes"]:
                if size["available"] is True:
                    sizes[size["slug"]] = {
                        "description": size["description"],
                        "price": f"${size['price_hourly']}/hr",
                    }

            if not resp["links"] or "last" not in resp["links"]["pages"]:
                break

            page += 1

        return sizes

    @authorized
    def valid_image_in_region(self, image: str, region: str) -> bool:
        """Check if the image/region combination is valid."""
        page = 1
        while True:
            resp = requests.get(
                f"{DigitalOcean.API_URL}/images?per_page=500&page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for i in resp["images"]:
                if i["slug"] == image:
                    # image is in region and available
                    return region in i["regions"] and i["status"] == "available"

            if not resp["links"] or "last" not in resp["links"]["pages"]:
                break

            page += 1

        return False

    @authorized
    def valid_resource_in_region(self, resource: str, region: str) -> bool:
        """Check if the resource type is available in the region."""
        page = 1
        while True:
            resp = requests.get(
                f"{DigitalOcean.API_URL}/sizes?per_page=500&page={page}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for size in resp["sizes"]:
                if size["slug"] == resource:
                    # resource is in region and available
                    return region in size["regions"] and size["available"] is True

            if not resp["links"] or "last" not in resp["links"]["pages"]:
                break

            page += 1

        return False

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return the SSH user."""
        return "root"
