#!/usr/bin/env python3

from pkg_resources import resource_filename
from boto3.session import Session
from typing import List, Dict
import boto3
import json


class aws:
    
    # Translate region code to region name. Even though the API data contains
    # regionCode field, it will not return accurate data. However using the location
    # field will, but then we need to translate the region code into a region name.
    # You could skip this by using the region names in your code directly, but most
    # other APIs are using the region code.
    def get_region_name(region_code):
        default_region = 'US East (N. Virginia)'
        endpoint_file = resource_filename('botocore', 'data/endpoints.json')
        try:
            with open(endpoint_file, 'r') as f:
                data = json.load(f)
            # Botocore is using Europe while Pricing API using EU...sigh...
            return data['partitions'][0]['regions'][region_code]['description'].replace('Europe', 'EU')
        except IOError:
            return default_region


    @staticmethod 
    def authorized(api_token: dict) -> bool:
        try:
            access_key = api_token['access_key']
            secret_key = api_token['secret_key']

            client = boto3.client(
                'sts',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )
            client.get_caller_identity()
            return True
        except Exception as e:
            print(e)
            return False
    

    @staticmethod 
    def get_images(api_token: dict, region: str = 'us-east-1') -> Dict:
        return {
            'ami-0f9fc25dd2506cf6d': 'Amazon Linux 2',
            'ami-0d6e9a57f6259ba3a': 'Centos 8',
            'ami-02358d9f5245918a3': 'Centos 7 ',
            'ami-0d35afd5d19280755': 'Debian 11',
            'ami-059e59467656af55e': 'Debian 10',
            'ami-03f9e5587a7d588f8': 'Debain 9',
            'ami-01691107cfcbce68c': 'Kali',
            'ami-0ec1545979d0dc885': 'Rocky 8',
            'ami-04505e74c0741db8d': 'Ubuntu 20.04',
            'ami-0e472ba40eb589f49': 'Ubuntu 18.04',
            'ami-0b0ea68c435eb488d': 'Ubuntu 16.04',
            
        }
        # below is how to query API, but 2k+ items are returned
        images = dict()

        access_key = api_token['access_key']
        secret_key = api_token['secret_key']
        client = boto3.client('ec2', 
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region)
        resp = client.describe_images(
                    Owners=[
                        '099720109477',
                        '679593333241',
                    ],
                    Filters=[
                        {
                            'Name': 'architecture',
                            'Values': ['x86_64']
                        },
                        {
                            'Name': 'state',
                            'Values': ['available']
                        }
                    ], IncludeDeprecated=False)

        # print(resp)
        for image in resp['Images']:
            try:
                images[image['ImageId']] = image['Description']
            except KeyError as e:
                pass

        print(len(images))
        return images
    
    @staticmethod
    def get_resources(api_token: dict, region: str = 'us-east-1') -> Dict:
        instances = dict()

        # get_products function of the Pricing API
        FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'\
              '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'\
              '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},'\
              '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'

        access_key = api_token['access_key']
        secret_key = api_token['secret_key']

        client = boto3.client('pricing', 
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region)

        f = FLT.format(r=aws.get_region_name(region))
    
        resp = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f))

        for instance in resp['PriceList']:
            instance = json.loads(instance)

            price = ''
            for _,v in instance['terms']['OnDemand'].items():
                for _,v2 in v['priceDimensions'].items():
                    price_desc = v2['description'].split(' ')
                    price = f"{price_desc[0]}/{price_desc[-1]}"


            try:
                mem = instance['product']['attributes']['memory']
                vcpu = instance['product']['attributes']['vcpu']
                description = f"{vcpu}VCpu {mem}"

                instances[instance['product']['attributes']['instanceType']] = {
                    'description': description,
                    'price': price
                }
            except KeyError as e:
                print(instance)
                exit()

        return instances
    


    @staticmethod 
    def get_regions(api_token: dict) -> List:
        regions = dict()

        session = Session()
        resp = session.get_available_regions('ec2') 

        for region in resp:
            regions[region] = region

        return regions
    

    @staticmethod 
    def valid_image_in_region(image: str, region: str, token: str) -> Dict:
        images = aws.get_images(token, region)
        
        if image in images.keys():
            return True

        return False


    @staticmethod 
    def valid_resource_in_region(resource: str, region: str, token: str) -> bool:
        return True  
