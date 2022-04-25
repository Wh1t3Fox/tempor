#!/usr/bin/env python3

from typing import Dict
import requests
import json


API_URL = 'https://api.digitalocean.com/v2'

class digitalocean:

    def get_account(token: str) -> Dict:
        return requests.get(f'{API_URL}/account', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()


    @staticmethod 
    def authorized(token: str) -> bool:
        resp = digitalocean.get_account(token)
    
        if 'id' in resp and resp['id'] == 'Unauthorized':
            return False
    
        return True
    
    
    @staticmethod 
    def get_images(token: str) -> Dict:
        images = dict()

        page = 1
        while True:
            resp = requests.get(f'{API_URL}/images?per_page=500&page={page}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()


            for image in resp['images']:
                images[image['slug']] = image['name']

            if not resp['links'] or 'last' not in resp['links']['pages']:
                break

            page += 1

        return images
    

    @staticmethod 
    def valid_image_in_region(image: str, region: str, token: str) -> Dict:
        images = list()

        page = 1
        while True:
            resp = requests.get(f'{API_URL}/images?per_page=500&page={page}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()


            for i in resp['images']:
                if i['slug'] == image:
                    # image is in region and available
                    return region in i['regions'] and i['status'] == 'available'

            if not resp['links'] or 'last' not in resp['links']['pages']:
                break

            page += 1

        return False


    @staticmethod 
    def get_regions(token: str) -> Dict:
        regions = dict()

        page = 1
        while True:
            resp = requests.get(f'{API_URL}/regions?per_page=500&page={page}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()

            for region in resp['regions']:
                if region['available'] == True:
                    regions[region['slug']] = region['name']

            if not resp['links'] or 'last' not in resp['links']['pages']:
                break

            page += 1

        return regions
