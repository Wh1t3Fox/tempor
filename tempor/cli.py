#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import *
import argparse
import logging
import sys

from tempor import ROOT_DIR
from tempor.ssh import (
        check_sshkeys,
        install_ssh_keys
)
from tempor.utils import (
    get_config,
    terraform_installed
)

logger = logging.getLogger(__name__)

def get_args():
    cfg = get_config()

    if not cfg:
        sys.exit(1)

    if 'default' in cfg:
        provider = cfg['default']
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--provider',
        default=provider,
        help='Specify the Provider Name'
    )
    parser.add_argument(
        '--teardown',
        action='store_true',
        help='Tear down VPS'
    )

    args = parser.parse_args()

    # Check if provider is set
    if not args.provider:
        logger.error('Must Specify a Provider')
        sys.exit(1)

    provider = args.provider
    if 'providers' in cfg:
        # lets check for the API token
        try:
            api_token = [i['api_token'] for i in cfg['providers'] if i['name'] == provider][0]
        except IndexError:
            logger.error('API Tokns are required')
            sys.exit(1)
    else:
        logger.error('Providers are required')
        sys.exit(1)

    return (provider, api_token, args)


def main():
    provider, api_token, args = get_args()
    terr_path = terraform_installed()

    t = Terraform(
        working_dir=f'{ROOT_DIR}/providers/{provider}',
        variables={'api_token':api_token},
        terraform_bin_path=terr_path
    )
    # make sure terraform is initialized
    ret, stdout, stderr = t.init()
    logger.debug(f'{ret}\n{stdout}\n{stderr}')
    if ret != 0 and stderr:
        logger.error('Failed during initialization')
        logger.error(stderr)
        return
    
    # now what do we want to do?
    if args.teardown:
        sys.stdout.write('[i] Tearing down...')
        sys.stdout.flush()
        ret, stdout, stderr = t.destroy()
        logger.debug(f'{ret}\n{stdout}\n{stderr}')
        if ret != 0 and stderr:
            logger.error('Failed during Teardown')
            logger.error(stderr)
        sys.stdout.write('Done.\n')
        sys.stdout.flush()
        return

    if check_sshkeys(provider) is False:
        return

    # lets plan the config
    sys.stdout.write('[i] Preparing Configuration...')
    sys.stdout.flush()
    plan_path = f'{ROOT_DIR}/providers/{provider}/files/plan'
    ret, stdout, stderr = t.cmd('plan', f'-out={plan_path}', var={'api_token':api_token})
    logger.debug(f'{ret}\n{stdout}\n{stderr}')
    if ret != 0 and stderr:
        logger.error('Failed during Planning')
        logger.error(stderr)
        return
    sys.stdout.write('Done.\n')
    sys.stdout.flush()

    # now apply the config
    sys.stdout.write('[i] Creating VPS...')
    sys.stdout.flush()
    ret, stdout, stderr = t.cmd('apply', plan_path)
    logger.debug(f'{ret}\n{stdout}\n{stderr}')
    if ret != 0 and stderr:
        logger.error('Failed during Applying')
        logger.error(stderr)
        return
    sys.stdout.write('Done.\n')
    sys.stdout.flush()

    sys.stdout.write('[i] Configuring SSH Keys...')
    sys.stdout.flush()
    # Get Hostname and IP Adress
    output = t.output()
    if 'droplet_ip_address' in output:
        hostname, ip_address = tuple(output['droplet_ip_address']['value'].items())[0]
    elif 'instance_ip_address' in output:
        hostname, ip_address = tuple(output['instance_ip_address']['value'].items())[0]
    elif 'server_ip_address' in output:
        hostname, ip_address = tuple(output['server_ip_address']['value'].items())[0]

    install_ssh_keys(provider, hostname, ip_address)
    sys.stdout.write('Done.\n')
    sys.stdout.flush()

    logger.info('Access to VPS now available:')
    logger.info(f'ssh {hostname}')


if __name__ == '__main__':
    main()
