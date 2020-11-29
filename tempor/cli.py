#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from python_terraform import *
import argparse
import logging
import json
import sys

from tempor import ROOT_DIR
from tempor.ssh import (
        check_sshkeys,
        install_ssh_keys
)
from tempor.utils import (
    get_config,
    get_hosts,
    rm_hosts,
    save_hosts,
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
        '-c',
        '--count',
        default=1,
        type=int,
        help='Number of Images to Create'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup Image(s)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List Available Images'
    )
    parser.add_argument(
        '--no-config',
        action='store_true',
        help='Leave as a Bare Install'
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
        rm_hosts(provider)
        sys.stdout.write('Done.\n')
        sys.stdout.flush()
        return

    elif args.list:
        all_hosts = get_hosts()
        if provider in all_hosts:
            for host, ip in all_hosts[provider].items():
                logger.info(f'{host}\t{ip}')
        return

    # prevent accidental creations
    if not args.setup:
        return

    if check_sshkeys(provider) is False:
        return

    # lets plan the config
    sys.stdout.write('[i] Preparing Configuration...')
    sys.stdout.flush()
    plan_path = f'{ROOT_DIR}/providers/{provider}/files/plan'
    ret, stdout, stderr = t.cmd('plan', f'-out={plan_path}', var={'api_token':api_token, 'num':args.count})
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
    
    new_hosts = dict()
    if 'droplet_ip_address' in output:
        for hostname,ip_address in output['droplet_ip_address']['value'].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)
            
    elif 'instance_ip_address' in output:
        for hostname,ip_address in output['instance_ip_address']['value'].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)

    elif 'server_ip_address' in output:
        for hostname,ip_address in output['server_ip_address']['value'].items():
            new_hosts[hostname] = ip_address
            install_ssh_keys(provider, hostname, ip_address)

    sys.stdout.write('Done.\n')
    sys.stdout.flush()

    logger.info('SSH Access to VPS now available for:')
    for host in new_hosts:
        logger.info(f'ssh {host}')

    save_hosts(provider, new_hosts)

if __name__ == '__main__':
    main()
