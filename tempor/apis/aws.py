#!/usr/bin/env python3
"""AWS API."""

import importlib.resources
import logging
import boto3
import json

# Change logging levels
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

class aws:
    """AWS API Class."""

    def __init__(self, api_token: dict, region: str = 'us-east-1'):
        self.logger = logging.getLogger(__name__)
        self.api_token = api_token
        self.access_key = self.api_token.get("access_key", None)
        self.secret_key = self.api_token.get("secret_key", None)
        self.profile = self.api_token.get("profile", None)

        self.region = region

        self.session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            profile_name=self.profile,
            region_name=self.region,
        )

    def is_authorized(self) -> bool:
        """Check if API tokens are valid."""
        try:
            client = self.session.client("sts")
            client.get_caller_identity()
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def get_images(self, region: str = "us-east-1") -> dict:
        """Return available AMI images for the region."""
        images = {}

        client = self.session.client("ec2")
        resp = client.describe_images(
            Owners=["amazon", "aws-marketplace"],
            Filters=[
                {"Name": "state", "Values": ["available"]},
                {
                    "Name": "name",
                    "Values": [
                        "al2023-ami-2023.7.20250331.0-kernel-6.1-x86_64",
                        "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-20250305",
                        "debian-12-amd64-20250316-2053",
                    ],
                },
            ],
        )

        for image in resp["Images"]:
            try:
                images[image["ImageId"]] = image["Description"]
            except KeyError:
                pass

        return images

    def get_resources(self, region: str = "us-east-1") -> dict:
        """Return available EC2 hardware types ."""
        instances = {}

        # get_products function of the Pricing API
        FLT = (
            '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'
            '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'
            '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},'
            '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'
        )

        client = boto3.client("pricing")

        f = FLT.format(r=aws.get_region_name(region))

        # this only works with cerain regions apparently
        try:
            resp = client.get_products(ServiceCode="AmazonEC2", Filters=json.loads(f))
        except Exception:
            self.logger.debug(f'Region {region} not supported... using us-east-1.')
            return self.get_resources('us-east-1')

        for instance in resp["PriceList"]:
            instance = json.loads(instance)

            price = ""
            for _, v in instance["terms"]["OnDemand"].items():
                for _, v2 in v["priceDimensions"].items():
                    price_desc = v2["description"].split(" ")
                    price = f"{price_desc[0]}/{price_desc[-1]}"

            try:
                mem = instance["product"]["attributes"]["memory"]
                vcpu = instance["product"]["attributes"]["vcpu"]
                description = f"{vcpu}VCpu {mem}"

                instances[instance["product"]["attributes"]["instanceType"]] = {
                    "description": description,
                    "price": price,
                }
            except KeyError:
                self.logger.error(instance)
                exit()

        return instances

    def get_regions(self) -> dict:
        """Return all possible regions."""
        regions = {}

        resp = self.session.get_available_regions("ec2")

        for region in resp:
            regions[region] = region

        return regions

    def valid_image_in_region(self, image: str, region: str) -> bool:
        """Validate if the AMI is in the correct region."""
        client = boto3.client("ec2", region_name=region)

        try:
            # Exception is thrown if the image is not in this region
            client.describe_images(
                ImageIds=[image],
                Filters=[
                    {"Name": "state", "Values": ["available"]},
                ],
            )
        except Exception as e:
            self.logger.debug(e)
            return False
        return True

    def valid_resource_in_region(self,resource: str, region: str) -> bool:
        """All resources exist in all regions."""
        return True

    @staticmethod
    def get_user(image: str, region: str) -> str:
        """Try to determine the correct SSH user for the AMI."""
        client = boto3.client("ec2")

        try:
            # Exception is thrown if the image is not in this region
            resp = client.describe_images(
                ImageIds=[image],
                Filters=[
                    {"Name": "state", "Values": ["available"]},
                ],
            )
            ami = resp.get("Images")[0]
            ami_name = ami.get("Name").lower()

            platform = ami.get("Platform", "").lower()
            owner = ami.get("ImageOwnerAlias", "")

            if platform == "windows":
                return "Administrator"

            if "amazon" in owner or owner == "aws-marketplace":
                if "amzn" in ami_name:
                    return "ec2-user"
                elif "ubuntu" in ami_name:
                    return "ubuntu"
                elif "centos" in ami_name:
                    return "centos"
                elif "fedora" in ami_name:
                    return "fedora"
                elif "rhel" in ami_name:
                    return "ec2-user"
                else:
                    return "ec2-user"
            else:
                return "ec2-user"

        except Exception:
            return "ec2-user"
        return "ec2-user"

    @staticmethod
    def get_region_name(region_code: str) -> str:
        """Translate region name.

        Translate region code to region name. Even though the API data contains
        regionCode field, it will not return accurate data. However using the location
        field will, but then we need to translate the region code into a region name.
        You could skip this by using the region names in your code directly, but most
        other APIs are using the region code.

        """
        default_region = "US East (N. Virginia)"
        ref = importlib.resources.files("botocore") / "data/endpoints.json"
        with importlib.resources.as_file(ref) as endpoint_file:
            try:
                with open(endpoint_file) as f:
                    data = json.load(f)
                # Botocore is using Europe while Pricing API using EU...sigh...
                return data["partitions"][0]["regions"][region_code][
                    "description"
                ].replace("Europe", "EU")
            except OSError:
                return default_region

