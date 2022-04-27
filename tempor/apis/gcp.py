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
        #return {
        #    'ubuntu-os-cloud/ubuntu-2004-lts': 'Ubuntu 20.04',
        #    'ubuntu-os-cloud/ubuntu-1804-lts': 'Ubuntu 18.04'
        #}
        images = dict()

        auth_file = api_token['auth_file']
        proj = api_token['project']

        creds, _ = google.auth.load_credentials_from_file(auth_file)
        service = discovery.build('compute', 'v1', credentials=creds)

        # this is stupid see https://issuetracker.google.com/issues/64718267?pli=1
        # https://cloud.google.com/compute/docs/images/os-details
        projects = [
            proj,
            'centos-cloud',
            'debian-cloud',
            'fedora-coreos-cloud',
            'rocky-linux-cloud',
            'ubuntu-os-cloud',
            'ubuntu-os-pro-cloud',
        ]

        for project in projects:
            resp = service.images().list(project=project).execute()
            
            if 'items' not in resp:
                continue
            
            for image in resp['items']:
                # ignore the deprecated and obsolete images
                if 'deprecated' in image and \
                        'state' in image['deprecated'] and \
                        image['deprecated']['state'] in ['OBSOLETE', 'DEPRECATED']:
                            continue

                '''
                The image from which to initialize this disk. 
                This can be one of: the image's self_link, 
                projects/{project}/global/images/{image}, 
                projects/{project}/global/images/family/{family}, 
                global/images/{image}, global/images/family/{family}, 
                family/{family}, {project}/{family}, 
                {project}/{image}, {family}, or {image}
                '''
                try:
                    _image = f'{project}/{image["family"]}'
                    images[_image] = image['description']
                except:
                    _image = f'{project}/{image["name"]}'
                    images[_image] = image['name']


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
        
        resp = service.regions().list(project=project).execute()
        for region in resp['items']:
            if region['status'] == 'UP':
                regions[region['name']] = [z.split('zones/')[-1] for z in region['zones']]

        return regions
