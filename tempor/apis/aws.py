#!/usr/bin/env python3

from boto3.session import Session
from typing import List, Dict
import boto3


class aws:

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
    def valid_image_in_region(image: str, region: str, token: str) -> Dict:
        images = aws.get_images(token, region)
        
        if image in images.keys():
            return True

        return False
    

    @staticmethod 
    def get_regions(api_token: dict) -> List:
        regions = dict()

        session = Session()
        resp = session.get_available_regions('ec2') 

        for region in resp:
            regions[region] = region

        return regions
