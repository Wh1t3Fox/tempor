#!/usr/bin/env python3

from googleapiclient import discovery
import google.auth

from typing import List, Dict


class gcp:

    @staticmethod 
    def authorized(api_token: dict) -> bool:
        try:
            auth_file = api_token['auth_file']

            google.auth.load_credentials_from_file(auth_file)

            return True
        except Exception as e:
            print(e)
            return False
    
    
    @staticmethod 
    def get_images(api_token: dict) -> Dict:
        images = dict()

        auth_file = api_token['auth_file']

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build('compute', 'v1', credentials=creds)

        # this is stupid see https://issuetracker.google.com/issues/64718267?pli=1
        projects = [
            #'centos-cloud',
            #'debian-cloud',
            'ubuntu-os-cloud',
        ]

        for project in projects:
            req = service.images().list(project=project,
                    filter='(deprecated.state="ACTIVE")')
            while req is not None:
                resp = req.execute()
                print(resp)

                for image in resp['items']:
                    print(image)
                    #if 'deprecated' in image and \
                    #        'state' in image['deprecated'] and \
                    #        image['deprecated']['state'] in ['OBSOLETE', 'DEPRECATED']:
                    #            continue

                    _image = f'{project}/{image["family"]}'

                    if _image in images:
                        continue

                    images[_image] = image['description']

        return images
    

    @staticmethod 
    def valid_image_in_region(image: str, region: str, token: str) -> Dict:
        return True
    

    @staticmethod 
    def get_regions(api_token: dict) -> List:
        regions = dict()

        auth_file = api_token['auth_file']
        project = api_token['project']

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build('compute', 'v1', credentials=creds)
        
        req = service.regions().list(project=project)
        while req is not None:
            resp = req.execute()

            for region in resp['items']:
                if region['status'] == 'UP':
                    regions[region['name']] = region['zones']

        return regions
