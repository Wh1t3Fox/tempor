#!/usr/bin/env python3

from typing import Dict
import requests
import json


API_URL = 'https://api.vultr.com/v2'

class vultr:

    def get_account(token: str) -> Dict:
        return requests.get(f'{API_URL}/account', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
    

    @staticmethod 
    def authorized(token: str) -> bool:
        resp = vultr.get_account(token)
    
        if 'error' in resp:
            return False
    
        return True
    
    
    @staticmethod 
    def get_images(token: str) -> Dict:
        images = dict()

        cursor = ''
        while True:
            resp =  requests.get(f'{API_URL}/os{cursor}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()


            for image in resp['os']:
                images[image['id']] = image['name']

            if 'links' not in resp['meta'] or not resp['meta']['links']['next']:
                break
            else:
                cursor = '?cursor=' + resp['meta']['links']['next']

        return images


    @staticmethod 
    def get_regions(token: str) -> Dict:
        regions = dict()

        cursor = ''
        while True:
            resp = requests.get(f'{API_URL}/regions{cursor}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
            
            for region in resp['regions']:
                regions[region['id']] = f'{region["city"]}, {region["country"]}'

            if 'links' not in resp['meta'] or not resp['meta']['links']['next']:
                break
            else:
                cursor = '?cursor=' + resp['meta']['links']['next']

        return regions


    @staticmethod 
    def get_resources(token: str) -> Dict:
        types = {
            'vc2': 'Cloud Compute',
            'vdc': 'Dedicated Cloud',
            'vhf': 'High Frequency Compute',
            'vhp': 'High Performance',
            'voc': 'All Optimized Cloud Types',
            'voc-g': 'General Purpose Optimized Cloud',
            'voc-c': 'CPU Optimized Cloud',
            'voc-m': 'Memory Optimized Cloud',
            'voc-s': 'Storage Optimized Cloud'
        }

        plans = dict()

        cursor = ''
        while True:
            resp = requests.get(f'{API_URL}/plans{cursor}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
            
            for plan in resp['plans']:
                plans[plan['id']] = {
                    'description': types[plan['type']],
                    'price': f"${plan['monthly_cost']}/month"
                }

            if 'links' not in resp['meta'] or not resp['meta']['links']['next']:
                break
            else:
                cursor = '?cursor=' + resp['meta']['links']['next']

        return plans
   

    @staticmethod 
    def valid_image_in_region(image: str, region: str, token: str) -> bool:
        return True  # vultr does not restrict images in regions
    

    @staticmethod 
    def valid_resource_in_region(resource: str, region: str, token: str) -> bool:
        cursor = ''
        while True:
            resp = requests.get(f'{API_URL}/plans{cursor}', headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                        }).json()
            
            for plan in resp['plans']:
                if resource == plan['id']:
                    return region in plan['locations']

            if 'links' not in resp['meta'] or not resp['meta']['links']['next']:
                break
            else:
                cursor = '?cursor=' + resp['meta']['links']['next']

        return False
