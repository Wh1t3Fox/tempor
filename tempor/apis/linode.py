#!/usr/bin/env python3
"""Linode API."""

import requests

class linode:
    """Linode API Class."""

    API_URL = "https://api.linode.com/v4"

    @staticmethod
    def get_account(token: str) -> dict:
        """Get account information."""
        return requests.get(
            f"{linode.API_URL}/account",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        ).json()

    @staticmethod
    def authorized(token: str) -> bool:
        """Check if API token is valid."""
        resp = linode.get_account(token)

        if "errors" in resp:
            return False

        return True

    @staticmethod
    def get_images(token: str) -> dict:
        """Get available images."""
        images = {}

        page = 1
        while True:
            resp = requests.get(
                f"{linode.API_URL}/images?page={page}",
                headers={
                    "Authorization": f"Bearer {token}",
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

    @staticmethod
    def get_regions(token: str) -> dict:
        """Get available regions."""
        regions = {}

        page = 1
        while True:
            resp = requests.get(
                f"{linode.API_URL}/regions?page={page}",
                headers={
                    "Authorization": f"Bearer {token}",
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

    @staticmethod
    def get_resources(token: str) -> dict:
        """Get available resource types."""
        types = {}

        page = 1
        while True:
            resp = requests.get(
                f"{linode.API_URL}/linode/types?page={page}",
                headers={
                    "Authorization": f"Bearer {token}",
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

    @staticmethod
    def valid_image_in_region(image: str, region: str, token: str) -> bool:
        """Linode does not restrict images in regions."""
        return True

    @staticmethod
    def valid_resource_in_region(resource: str, region: str, token: str) -> bool:
        """Linode does not restrict types in regions."""
        return True

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return SSH user."""
        return "root"
