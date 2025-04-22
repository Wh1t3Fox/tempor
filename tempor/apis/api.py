#!/usr/bin/env python3
"""Parent Class Defintion.

Each VPS Provider needs to impliment
these functions to properly operate.
"""

import logging

from .helpers import authorized

class API:
    """Parent Class."""

    def __init__(self, api_token, region):
        self.logger = logging.getLogger(__name__)
        self.api_token = api_token
        self.region = region

    def is_authorized(self) -> bool:
        """Check if API tokens are valid."""
        return True

    @authorized
    def get_images(self, region) -> dict:
        """Return available images for the region."""
        return {}

    @authorized
    def get_resources(self, region) -> dict:
        """Return available hardware types."""
        return {}

    @authorized
    def get_regions(self) -> dict:
        """Return all possible regions."""
        return {}

    @authorized
    def valid_image_in_region(self, image, region) -> bool:
        """Validate if the Image is in the correct region."""
        return True

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Try to determine the correct SSH user for the Image."""
        return "root"

