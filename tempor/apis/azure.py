#!/usr/bin/env python3
"""Azure API."""

import requests

from .api import API
from .helpers import authorized

class Azure(API):
    """Azure API Class."""

    API_URL = "https://management.azure.com"

    def __init__(self, api_token: dict, region: str = ''):
        super().__init__(api_token, region)
        self.oauth_token = self.get_auth_token().get("access_token", "")

    def get_auth_token(self) -> dict:
        """Return auth token."""
        return requests.post(
            f'https://login.microsoftonline.com/{self.api_token["tenant_id"]}/oauth2/token',
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_token["client_id"],
                "client_secret": self.api_token["client_secret"],
                "resource": Azure.API_URL,
            },
        ).json()

    def is_authorized(self) -> bool:
        """Check if API token is valid."""
        try:
            resp = self.get_auth_token()
        except Exception:
            return False

        if "error" in resp:
            return False

        self.oauth_token = resp["access_token"]

        return True

    @authorized
    def get_offers(self, publisher: str, location: str) -> list:
        """Get available offers."""
        offers = []

        resp = requests.get(
            f"{Azure.API_URL}/subscriptions/{self.api_token['subscription']}/providers/Microsoft.Compute/locations/{location}/publishers/{publisher}/artifacttypes/vmimage/offers?api-version=2022-03-01",
            headers={
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        for offer in resp:
            try:
                # test-ubuntu-premium-offer-0002
                if offer["name"].startswith("test"):
                    continue

                # 0001-com-ubuntu-confidential-vm-test-focal
                int(offer["name"].split("-")[0])

            except Exception:
                offers.append(offer["name"])

        return offers

    @authorized
    def get_skus(self, publisher: str, location: str, offer: str) -> list:
        """Get available SKUs."""
        resp = requests.get(
            f"{Azure.API_URL}/subscriptions/{self.api_token['subscription']}/providers/Microsoft.Compute/locations/{location}/publishers/{publisher}/artifacttypes/vmimage/offers/{offer}/skus?api-version=2022-03-01",
            headers={
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        return [sku["name"] for sku in resp]

    @authorized
    def get_images(self, region="eastus") -> dict:
        """Get available images."""
        images = {}

        for publisher in ["Canonical", "Debian"]:
            # Gets Offers
            offers = self.get_offers(publisher, region)


            # Query skus
            for offer in offers:
                skus = self.get_skus(publisher, region, offer)

                # populate images: {publisher}/{offer}/{sku}
                for sku in skus:
                    image = f"{publisher}/{offer}/{sku}"
                    images[image] = f"{offer} {sku}"

        return images

    @authorized
    def get_regions(self) -> dict:
        """Get available regions."""
        regions = {}

        # Need to figure out pagination, but in sample test it was a single page
        resp = requests.get(
            f'{Azure.API_URL}/subscriptions/{self.api_token["subscription_id"]}/locations?api-version=2022-01-01',
            headers={
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        for region in resp["value"]:
            try:
                regions[region["name"]] = region["displayName"]
            except Exception:
                pass

        return regions

    @authorized
    def get_price(self, region: str) -> dict:
        """Get price."""
        prices = {}

        res = requests.get(
            "https://prices.azure.com/api/retail/prices?$filter=armRegionName%20eq%20%27eastus%27%20and%20serviceFamily%20eq%20%27Compute%27%20and%20tierMinimumUnits%20eq%200"
        ).json()

        # TODO there are multiple skunames with different prices :/
        for item in res["Items"]:
            prices[item["armSkuName"]] = item["unitPrice"]

        return prices

    @authorized
    def get_resources(self, region: str) -> dict:
        """Get available resources."""
        sizes = {}

        prices = self.get_price(region)

        # Need to figure out pagination, but in sample test it was a single page
        resp = requests.get(
            f'{Azure.API_URL}/subscriptions/{self.api_token["subscription_id"]}/providers/Microsoft.Compute/locations/{region}/vmSizes?api-version=2022-03-01',
            headers={
                "Authorization": f"Bearer {self.oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        for size in resp["value"]:
            description = f"{size['numberOfCores']} Cores {size['memoryInMB']//1024}Gb"

            sizes[size["name"]] = {
                "description": description,
                "price": prices.get(size["name"], "UNK"),
            }

        return sizes

    @authorized
    def valid_image_in_region(self, image: str, region: str) -> bool:
        """Check if image is in the correct region."""
        images = self.get_images(region)

        if image in images:
            return True

        return False

    @authorized
    def valid_resource_in_region(self, resource: str, region: str) -> bool:
        """Is  the resource type in the correct region."""
        resources = self.get_resources(region)

        if resource in resources:
            return True

        return False

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return user."""
        return "root"
