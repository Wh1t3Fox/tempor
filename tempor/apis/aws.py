#!/usr/bin/env python3
"""AWS API."""

import importlib.resources
import boto3
import json


class aws:
    """AWS API Class."""

    # Translate region code to region name. Even though the API data contains
    # regionCode field, it will not return accurate data. However using the location
    # field will, but then we need to translate the region code into a region name.
    # You could skip this by using the region names in your code directly, but most
    # other APIs are using the region code.
    @staticmethod
    def get_region_name(region_code: str) -> str:
        """Translate region name."""
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

    @staticmethod
    def authorized(api_token: dict = {}) -> bool:
        """Check if API tokens are valid."""
        try:
            # None is the default value for these in the boto3 Session classs
            access_key = api_token.get("access_key", None)
            secret_key = api_token.get("secret_key", None)
            profile = api_token.get("profile", None)

            sess = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                profile_name=profile,
                region_name="us-east-1",
            )
            client = sess.client("sts")
            client.get_caller_identity()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_images(api_token: dict = {}, region: str = "us-east-1") -> dict:
        """Return available AMI images for the region."""
        images = {}

        # None is the default value for these in the boto3 Session classs
        access_key = api_token.get("access_key", None)
        secret_key = api_token.get("secret_key", None)
        profile = api_token.get("profile", None)

        sess = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            profile_name=profile,
            region_name=region,
        )
        client = sess.client("ec2")
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

    @staticmethod
    def get_resources(api_token: dict = {}, region: str = "us-east-1") -> dict:
        """Return available EC2 hardware types ."""
        instances = {}

        # get_products function of the Pricing API
        FLT = (
            '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'
            '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'
            '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},'
            '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'
        )

        access_key = api_token.get("access_key", None)
        secret_key = api_token.get("secret_key", None)
        profile = api_token.get("profile", None)

        sess = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            profile_name=profile,
            region_name=region,
        )
        client = sess.client("pricing")

        f = FLT.format(r=aws.get_region_name(region))

        # this only works with cerain regions apparently
        try:
            resp = client.get_products(ServiceCode="AmazonEC2", Filters=json.loads(f))
        except Exception:
            return aws.get_resources(api_token, 'us-east-1')

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
                print(instance)
                exit()

        return instances

    @staticmethod
    def get_regions(api_token: dict = {}) -> dict:
        """Return all possible regions."""
        access_key = api_token.get("access_key", None)
        secret_key = api_token.get("secret_key", None)
        profile = api_token.get("profile", None)

        regions = {}

        sess = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            profile_name=profile,
        )
        resp = sess.get_available_regions("ec2")

        for region in resp:
            regions[region] = region

        return regions

    @staticmethod
    def valid_image_in_region(image: str, region: str, api_token: dict = {}) -> bool:
        """Validate if the AMI is in the correct region."""
        access_key = api_token.get("access_key", None)
        secret_key = api_token.get("secret_key", None)
        profile = api_token.get("profile", None)

        sess = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            profile_name=profile,
            region_name=region,
        )
        client = sess.client("ec2")

        try:
            # Exception is thrown if the image is not in this region
            client.describe_images(
                ImageIds=[image],
                Filters=[
                    {"Name": "state", "Values": ["available"]},
                ],
            )
        except Exception:
            return False
        return True

    @staticmethod
    def valid_resource_in_region(
        resource: str, region: str, api_token: dict = {}
    ) -> bool:
        """All resources exist in all regions."""
        return True

    @staticmethod
    def get_user(image: str, region: str, api_token: dict = {}) -> str:
        """Try to determine the correct SSH user for the AMI."""
        access_key = api_token.get("access_key", None)
        secret_key = api_token.get("secret_key", None)
        profile = api_token.get("profile", None)

        sess = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            profile_name=profile,
            region_name=region,
        )
        client = sess.client("ec2")

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
