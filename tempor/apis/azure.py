#!/usr/bin/env python3
"""Azure API."""

import requests

class azure:
    """Azure API Class."""

    API_URL = "https://management.azure.com"

    @staticmethod
    def get_auth_token(token: dict) -> dict:
        """Return auth token."""
        return requests.post(
            f'https://login.microsoftonline.com/{token["tenant_id"]}/oauth2/token',
            data={
                "grant_type": "client_credentials",
                "client_id": token["client_id"],
                "client_secret": token["client_secret"],
                "resource": azure.API_URL,
            },
        ).json()

    @staticmethod
    def authorized(token: dict) -> bool:
        """Check if API token is valid."""
        resp = azure.get_auth_token(token)

        if "error" in resp:
            return False

        return True

    @staticmethod
    def get_offers(
        oauth_token: str, subscription: str, publisher: str, location: str
    ) -> list:
        """Get available offers."""
        offers = []

        resp = requests.get(
            f"{azure.API_URL}/subscriptions/{subscription}/providers/Microsoft.Compute/locations/{location}/publishers/{publisher}/artifacttypes/vmimage/offers?api-version=2022-03-01",
            headers={
                "Authorization": f"Bearer {oauth_token}",
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

    @staticmethod
    def get_skus(
        oauth_token: str, subscription: str, publisher: str, location: str, offer: str
    ) -> list:
        """Get available SKUs."""
        resp = requests.get(
            f"{azure.API_URL}/subscriptions/{subscription}/providers/Microsoft.Compute/locations/{location}/publishers/{publisher}/artifacttypes/vmimage/offers/{offer}/skus?api-version=2022-03-01",
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        return [sku["name"] for sku in resp]

    @staticmethod
    def get_images(token: dict, location="eastus") -> dict:
        """Get available images."""
        images = {}

        oauth_token = azure.get_auth_token(token)["access_token"]

        for publisher in ["Canonical", "Debian"]:
            # Gets Offers
            offers = azure.get_offers(
                oauth_token, token["subscription_id"], publisher, location
            )

            # Query skus
            for offer in offers:
                skus = azure.get_skus(
                    oauth_token, token["subscription_id"], publisher, location, offer
                )

                # populate images: {publisher}/{offer}/{sku}
                for sku in skus:
                    image = f"{publisher}/{offer}/{sku}"
                    images[image] = f"{offer} {sku}"

        return images

    @staticmethod
    def get_regions(token: dict) -> dict:
        """Get available regions."""
        regions = {}

        oauth_token = azure.get_auth_token(token)["access_token"]
        # Need to figure out pagination, but in sample test it was a single page
        resp = requests.get(
            f'{azure.API_URL}/subscriptions/{token["subscription_id"]}/locations?api-version=2022-01-01',
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "Content-Type": "application/json",
            },
        ).json()

        for region in resp["value"]:
            try:
                regions[region["name"]] = region["displayName"]
            except Exception:
                pass

        return regions

    @staticmethod
    def get_price(region: str) -> dict:
        """Get price."""
        prices = {}

        res = requests.get(
            "https://prices.azure.com/api/retail/prices?$filter=armRegionName%20eq%20%27eastus%27%20and%20serviceFamily%20eq%20%27Compute%27%20and%20tierMinimumUnits%20eq%200"
        ).json()

        # TODO there are multiple skunames with different prices :/
        for item in res["Items"]:
            prices[item["armSkuName"]] = item["unitPrice"]

        return prices

    @staticmethod
    def get_resources(token: dict, region: str) -> dict:
        """Get available resources."""
        sizes = {}

        oauth_token = azure.get_auth_token(token)["access_token"]

        prices = azure.get_price(region)

        # Need to figure out pagination, but in sample test it was a single page
        resp = requests.get(
            f'{azure.API_URL}/subscriptions/{token["subscription_id"]}/providers/Microsoft.Compute/locations/{region}/vmSizes?api-version=2022-03-01',
            headers={
                "Authorization": f"Bearer {oauth_token}",
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

    @staticmethod
    def valid_image_in_region(image: str, region: str, token: dict) -> bool:
        """Check if image is in the correct region."""
        images = azure.get_images(token, region)

        if image in images:
            return True

        return False

    @staticmethod
    def valid_resource_in_region(resource: str, region: str, token: dict) -> bool:
        """Is  the resource type in the correct region."""
        resources = azure.get_resources(token, region)

        if resource in resources:
            return True

        return False

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Return user."""
        return "root"
