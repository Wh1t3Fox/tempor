#!/usr/bin/env python3

from typing import Dict
import requests
import json


API_URL = 'https://api.linode.com/v4'

class linode:

    def get_account(token: str) -> Dict:
        return requests.get(f'{API_URL}/account', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
    

    @staticmethod 
    def authorized(token: str) -> bool:
        resp = linode.get_account(token)
    
        if 'errors' in resp:
            return False
    
        return True
    
    
    @staticmethod 
    def get_images(token: str) -> Dict:
        images = dict()

        page = 1
        while True:
            resp = requests.get(f'{API_URL}/images?page={page}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
            for image in resp['data']:
                if image['status'] == 'available':
                    images[image['id']] = image['label']


            if page == resp['pages']:
                break
            page += 1

        return images
    

    @staticmethod 
    def valid_image_in_region(image: str, region: str, token: str) -> Dict:
        return True  # linode does not restrict images in regions


    @staticmethod 
    def get_regions(token: str) -> Dict:
        regions = dict()

        page = 1
        while True:
            resp = requests.get(f'{API_URL}/regions?page={page}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()

            for region in resp['data']:
                if 'Linodes' in region['capabilities']:
                    regions[region['id']] = region['country']

            if page == resp['pages']:
                break
            page += 1

        return regions
