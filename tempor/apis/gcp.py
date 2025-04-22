#!/usr/bin/env python3
"""GCP API."""

from googleapiclient import discovery
import google.auth

from .api import API
from .helpers import authorized

class GCP(API):
    """GCP API Class."""

    def __init__(self, api_token: dict, region: str = ''):
        super().__init__(api_token, region)

    def is_authorized(self) -> bool:
        """Check if API token is valid."""
        try:
            auth_file = self.api_token["auth_file"]

            google.auth.load_credentials_from_file(auth_file)

            return True
        except Exception:
            return False

    @authorized
    def get_images(self, region: str = "") -> dict:
        """Get possible image types."""
        images = {}

        auth_file = self.api_token["auth_file"]
        proj = self.api_token["project"]

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build("compute", "v1", credentials=creds)

        # this is stupid see https://issuetracker.google.com/issues/64718267?pli=1
        # https://cloud.google.com/compute/docs/images/os-details
        projects = [
            proj,
            "centos-cloud",
            "debian-cloud",
            "fedora-coreos-cloud",
            "rocky-linux-cloud",
            "ubuntu-os-cloud",
            "ubuntu-os-pro-cloud",
        ]

        for project in projects:
            resp = service.images().list(project=project).execute()

            if "items" not in resp:
                continue

            for image in resp["items"]:
                # ignore the deprecated and obsolete images
                if (
                    "deprecated" in image
                    and "state" in image["deprecated"]
                    and image["deprecated"]["state"] in ["OBSOLETE", "DEPRECATED"]
                ):
                    continue

                """
                The image from which to initialize this disk.
                This can be one of: the image's self_link,
                projects/{project}/global/images/{image},
                projects/{project}/global/images/family/{family},
                global/images/{image}, global/images/family/{family},
                family/{family}, {project}/{family},
                {project}/{image}, {family}, or {image}
                """
                try:
                    _image = f'{project}/{image["family"]}'
                    images[_image] = image["description"]
                except Exception:
                    _image = f'{project}/{image["name"]}'
                    images[_image] = image["name"]

        return images

    @authorized
    def get_regions(self) -> dict:
        """Get possible regions."""
        regions = {}

        auth_file = self.api_token["auth_file"]
        project = self.api_token["project"]

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build("compute", "v1", credentials=creds)

        resp = service.regions().list(project=project).execute()
        for region in resp["items"]:
            if region["status"] == "UP":
                regions[region["name"]] = [
                    z.split("zones/")[-1] for z in region["zones"]
                ]

        return regions

    @authorized
    def get_resources(self, region: str) -> dict:
        """Get possible resource types."""
        machine_types = {}

        auth_file = self.api_token["auth_file"]
        project = self.api_token["project"]

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build("compute", "v1", credentials=creds)

        resp = service.machineTypes().list(project=project, zone=region).execute()

        for machine_type in resp["items"]:
            machine_types[machine_type["name"]] = {
                "description": machine_type["description"],
                "price": "UNK",
            }

        return machine_types

    @authorized
    def get_zones(self) -> list:
        """Get available zones."""
        auth_file = self.api_token["auth_file"]
        project = self.api_token["project"]

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build("compute", "v1", credentials=creds)

        resp = service.zones().list(project=project).execute()

        return [zone["name"] for zone in resp["items"]]

    @authorized
    def valid_zone(self, name: str) -> bool:
        """Get available zones."""
        auth_file = self.api_token["auth_file"]
        project = self.api_token["project"]

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build("compute", "v1", credentials=creds)

        resp = service.zones().list(project=project).execute()

        for zone in resp["items"]:
            if zone["name"] == name:
                return True

        return False

    @authorized
    def valid_image_in_region(self, image: str, region: str) -> bool:
        """All images types are in all regions."""
        return True

    @authorized
    def valid_resource_in_region(self,resource: str, region: str) -> bool:
        """All resources exist in all regions."""
        return True

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Get SSH user."""
        return "root"
