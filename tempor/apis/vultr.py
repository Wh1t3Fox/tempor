#!/usr/bin/env python3
"""Vultr API."""

import requests

class vultr:
    """Vultr API Class."""

    API_URL = "https://api.vultr.com/v2"

    def __init__(self, api_token: str, region: str = ''):
        self.api_token = api_token
        self.region = region

    def get_account(self) -> dict:
        """Get account information."""
        return requests.get(
            f"{vultr.API_URL}/account",
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        ).json()

    def authorized(self) -> bool:
        """Check if API token is valid."""
        resp = self.get_account()

        if "error" in resp:
            return False

        return True

    def get_images(self, region: str = "") -> dict:
        """Get available images."""
        images = {}

        cursor = ""
        while True:
            resp = requests.get(
                f"{vultr.API_URL}/os{cursor}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for image in resp["os"]:
                images[image["id"]] = image["name"]

            if "links" not in resp["meta"] or not resp["meta"]["links"]["next"]:
                break
            else:
                cursor = "?cursor=" + resp["meta"]["links"]["next"]

        return images

    def get_regions(self) -> dict:
        """Get available regions."""
        regions = {}

        cursor = ""
        while True:
            resp = requests.get(
                f"{vultr.API_URL}/regions{cursor}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for region in resp["regions"]:
                regions[region["id"]] = f'{region["city"]}, {region["country"]}'

            if "links" not in resp["meta"] or not resp["meta"]["links"]["next"]:
                break
            else:
                cursor = "?cursor=" + resp["meta"]["links"]["next"]

        return regions

    def get_resources(self, region: str = "") -> dict:
        """Get available resource types."""
        types = {
            "vc2": "Cloud Compute",
            "vdc": "Dedicated Cloud",
            "vhf": "High Frequency Compute",
            "vhp": "High Performance",
            "voc": "All Optimized Cloud Types",
            "voc-g": "General Purpose Optimized Cloud",
            "voc-c": "CPU Optimized Cloud",
            "voc-m": "Memory Optimized Cloud",
            "voc-s": "Storage Optimized Cloud",
        }

        plans = {}

        cursor = ""
        while True:
            resp = requests.get(
                f"{vultr.API_URL}/plans{cursor}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for plan in resp["plans"]:
                plans[plan["id"]] = {
                    "description": types[plan["type"]],
                    "price": f"${plan['monthly_cost']}/month",
                }

            if "links" not in resp["meta"] or not resp["meta"]["links"]["next"]:
                break
            else:
                cursor = "?cursor=" + resp["meta"]["links"]["next"]

        return plans

    def valid_image_in_region(self, image: str, region: str) -> bool:
        """Vultr does not restrict images in regions."""
        return True

    def valid_resource_in_region(self, resource: str, region: str) -> bool:
        """Check if the resource/region combination is valid."""
        cursor = ""
        while True:
            resp = requests.get(
                f"{vultr.API_URL}/plans{cursor}",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                },
            ).json()

            for plan in resp["plans"]:
                if resource == plan["id"]:
                    return region in plan["locations"]

            if "links" not in resp["meta"] or not resp["meta"]["links"]["next"]:
                break
            else:
                cursor = "?cursor=" + resp["meta"]["links"]["next"]

        return False

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return SSH user."""
        return "root"
