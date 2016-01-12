#!/usr/local/bin/python2.7

import applogger
import credentials
import os
import sys

from neutronclient.v2_0 import client

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))
credentials = credentials.get_credentials()
neutron = client.Client(**credentials)


def list_networks():
    '''
    Get a list for networks

    Returns:
        list.
    '''
    logger.info("0")
    netw = neutron.list_networks()
    logger.info("1")
    return netw['networks']


def create_network(network_name, cidr):
    '''
    Create a openstack network

    Args:
        network_name (str): set network name
        cidr (str): network subnet
    '''
    # Check if network name already taken
    existing_net = filter(lambda network: network['name'] == network_name, list_networks())
    if len(existing_net) > 0:
        raise ValueError('network name "%s" already taken. Please set a different network name' % network_name)
    else:
        logger.debug('Network name %s not taken. Creating network' % network_name)
        try:
            net_body = {'network': {'name': network_name, 'admin_state_up': True}}

            netw = neutron.create_network(body=net_body)
            net_dict = netw['network']
            network_id = net_dict['id']
            logger.info('Network %s created' % network_id)

            body_create_subnet = {'subnets': [{'cidr': cidr,
                                               'ip_version': 4, 'network_id': network_id}]}

            subnet = neutron.create_subnet(body=body_create_subnet)
            logger.info('Created subnet %s' % subnet)
        finally:
            logger.info('Execution completed')
            return subnet
