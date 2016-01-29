#!/usr/local/bin/python2.7

import applogger
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


def list_networks(login, network_name=None):
    '''
    Get a list for networks

    Returns:
        list.
    '''
    if network_name is None:
        neutron = client.Client(**login)
        netw = neutron.list_networks()
        return netw['networks']
    else:
        existing_net = filter(lambda network: network['name'] == network_name, list_networks(login))
        return existing_net


def list_devices(login, network_name):
    '''
    list compute devices on a network
    '''
    neutron = client.Client(**login)

    network = list_networks(login, network_name)
    if len(network) != 1:
        raise NameError('found %d networks with the name %s' % (len(network), network_name))
    else:
        devices = filter(lambda net_devices: net_devices['network_id'] == network[0]['id'] and
                         net_devices['device_owner'] != 'network:dhcp',
                         neutron.list_ports()['ports'])

        return devices


def create_network(login, network_name, cidr):
    '''
    Create a openstack network

    Args:
        login (dict): credentials for openstack
        network_name (str): set network name
        cidr (str): network subnet
    '''
    neutron = client.Client(**login)

    # Check if network name already taken
    existing_net = list_networks(login, network_name)
    if len(existing_net) > 0:
        raise ValueError('network name "%s" already taken. Please set a different network name' % network_name)
    else:
        logger.debug('Network name %s not taken. Creating network' % network_name)
        try:
            net_body = {'network': {'name': network_name, 'admin_state_up': True}}

            netw = neutron.create_network(body=net_body)
            network_id = netw['network']['id']
            logger.info('Network %s created' % network_id)
            subnet_name = '%s_subnet' % network_name
            body_create_subnet = {'subnets': [{'cidr': cidr,
                                               'name': subnet_name,
                                               'ip_version': 4,
                                               'network_id': network_id}]}

            subnet = neutron.create_subnet(body=body_create_subnet)
            logger.info('Created subnet %s' % subnet)
        finally:
            logger.info('Execution completed')
            return netw['network']


def delete_network(login, network_name):
    '''
    Delete an oprnstack network

    Args:
        login (dict): credentials for openstack
        network_name (str): set network name
    '''
    existing_net = list_networks(login, network_name)
    if len(existing_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(existing_net), network_name))
    elif len(existing_net) == 0:
        raise NameError('Could not find any network named %s' % network_name)
    else:
        logger.debug('Deleting network %s' % network_name)
        try:
            neutron = client.Client(**login)
            neutron.delete_network(existing_net[0]['id'])
        finally:
            logger.info('Network %s deleted from %s' % (network_name, login['region_name']))


def set_router(login, rtr_name, network, gw=None):
    '''
    creates a router connected to the relevant subnets
    '''
    neutron = client.Client(**login)

    # TODO: update method so that it can be used to add interface to existing routers
    body_value = {'router': {
        'name': rtr_name,
        'admin_state_up': True}
    }
    new_router = neutron.create_router(body=body_value)
    logger.info('Created router %s' % new_router)

    existing_net = list_networks(login, network)
    if len(existing_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(existing_net), network))
    elif len(existing_net) == 0:
        raise NameError('Could not find any network named %s' % network)
    else:
        neutron.add_interface_router(new_router['router']['id'], {'subnet_id': existing_net[0]['subnets'][0]})
        logger.info('Created interface on router %s' % new_router)

    gw_net = list_networks(login, gw)
    if len(gw_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(gw_net), gw))
    elif len(gw_net) == 0:
        raise NameError('Could not find any network named %s' % gw)
    else:
        gw_id = { 'network_id': gw_net[0]['id'] }
        neutron.add_gateway_router(new_router['router']['id'], gw_id)
        logger.info('Created gateway on router %s' % new_router)

    return new_router
