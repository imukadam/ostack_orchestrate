#!/usr/local/bin/python2.7

import applogger
import os
import sys
from time import sleep

import credentials
import nova

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))


def list_networks(session, network_name=None):
    '''
    Get a list for networks

    Returns:
        list.
    '''
    if network_name is None:
        netw = session.list_networks()
        return netw['networks']
    else:
        existing_net = filter(lambda network: network['name'] == network_name, list_networks(session))
        return existing_net


def list_devices(session, network_name):
    '''
    list devices on a network
    '''
    network = list_networks(session, network_name)
    if len(network) != 1:
        raise NameError('found %d networks with the name %s' % (len(network), network_name))
    else:
        devices = filter(lambda net_devices: net_devices['network_id'] == network[0]['id'],
                         session.list_ports()['ports'])

        return devices


def create_network(session, network_name, cidr, dns_nameservers):
    '''
    Create a openstack network

    Args:
        session (dict): credentials for openstack
        network_name (str): set network name
        cidr (str): network subnet
    '''
    # Check if network name already taken
    existing_net = list_networks(session, network_name)
    if len(existing_net) > 0:
        logger.error("Network name %s already taken. Please set a different network name" % network_name)
        raise ValueError("Network name %s already taken. Please set a different network name" % network_name)
    else:
        logger.debug("Network name %s not taken. Creating network" % network_name)
        try:
            net_body = {'network': {'name': network_name, 'admin_state_up': True}}

            netw = session.create_network(body=net_body)
            network_id = netw['network']['id']
            logger.info('Network %s created' % network_id)
            subnet_name = '%s_subnet' % network_name
            body_create_subnet = {'subnets': [{'cidr': cidr,
                                               'name': subnet_name,
                                               'dns_nameservers': dns_nameservers,
                                               'ip_version': 4,
                                               'network_id': network_id}]}

            subnet = session.create_subnet(body=body_create_subnet)
            logger.info('Created subnet %s' % subnet)
        finally:
            logger.info('Execution completed')
            return list_networks(session, netw['network']['name'])[0]


def delete_network(session, network_name):
    '''
    Delete an openstack network

    Args:
        session (dict): credentials for openstack
        network_name (str): set network name
    '''
    existing_net = list_networks(session, network_name)
    if len(existing_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(existing_net), network_name))
    elif len(existing_net) == 0:
        raise NameError('Could not find any network named %s' % network_name)
    else:
        devices = list_devices(session, network_name)
        router_interfaces = filter(lambda interface: interface['device_owner'] == 'network:router_interface', devices)
        if len(router_interfaces) > 0:
            for interface in router_interfaces:
                logger.info('Removing interface %s from router %s' % (interface['id'], interface['device_id']))
                interface_port = {'port_id': interface['id']}
                session.remove_interface_router(interface['device_id'], interface_port)
                sleep(5)  # Pause as the remove takes a bit of time to register

                if len(filter(lambda rtr_ports: rtr_ports['device_id'] == interface['device_id'], session.list_ports()['ports'])) == 0:
                    logger.info('Router %s not in use. Deleting it' % interface['device_id'])
                    delete_router(session, interface['device_id'])

        logger.debug('Deleting network %s' % network_name)
        try:
            session.delete_network(existing_net[0]['id'])
        except Exception, e:
            logger.fatal(str(e))
            raise e
        finally:
            logger.info('Network %s deleted' % network_name)


def set_router(session, rtr_name, network, gw=None):
    '''
    Creates a router connected to the relevant subnets
    '''
    # TODO: update method so that it can be used to add interface to existing routers
    body_value = {'router': {
        'name': rtr_name,
        'admin_state_up': True}
    }
    new_router = session.create_router(body=body_value)
    logger.info('Created router %s' % new_router)

    existing_net = list_networks(session, network)
    if len(existing_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(existing_net), network))
    elif len(existing_net) == 0:
        raise NameError('Could not find any network named %s' % network)
    else:
        session.add_interface_router(new_router['router']['id'], {'subnet_id': existing_net[0]['subnets'][0]})
        logger.info('Created interface on router %s' % new_router)

    gw_net = list_networks(session, gw)
    if len(gw_net) > 1:
        raise NameError('found %d networks with the name %s' % (len(gw_net), gw))
    elif len(gw_net) == 0:
        raise NameError('Could not find any network named %s' % gw)
    else:
        gw_id = {'network_id': gw_net[0]['id']}
        session.add_gateway_router(new_router['router']['id'], gw_id)
        logger.info('Created gateway on router %s' % new_router)

    return new_router


def delete_router(session, router_id):
    '''
    Deletes a router
    '''
    logger.info('Deleting router %s' % router_id)
    session.delete_router(router_id)
    sleep(5)  # Pause as the remove takes a bit of time to register


def list_lb_pools(session, pool_name=None):
    '''
    Returns a list of load balancers available on a tenant
    If pool_id is provided only that pool will be returned
    '''
    if pool_name is None:
        try:
            pools = session.list_pools()
            return pools['pools']
        except Exception, e:
            logger.fatal(str(e))
            raise e
    else:
        pool_filter = filter(lambda pool: pool['name'] == pool_name, list_lb_pools(session))
        if len(pool_filter) == 0:
            logger.error('Load balancer pool %s does not exist.' % pool_name)
            return None

        return pool_filter[0]


def create_lb_pool(session, name, subnet_id, provider='haproxy', protocol='HTTP', lb_method='ROUND_ROBIN'):
    '''
    Creates a new load balancer pool
    '''
    # Check id the lb name is unique
    existing_lb = list_lb_pools(session, name)
    if existing_lb:
        msg = "Load balancer name %s already taken. Please set a different name" % name
        logger.error(msg)
        raise ValueError(msg)
    else:
        logger.debug("Load balancer name %s not taken. Creating..." % name)
    logger.info('Creating load balancer %s' % name)
    pool_body = {'pool': {
             'name': name, 
             'provider': provider, 
             'subnet_id': subnet_id, 
             'protocol': protocol, 
             'lb_method': lb_method, 
             'admin_state_up': True}
    }

    lb_pool = session.create_pool(body=pool_body)

    if lb_pool:
        logger.info('Load balancer %s created sucessfully!' % name)
        return lb_pool['pool']
    else:
        msg = 'Could not create load balancer %s' % name
        logger.error(msg)
        raise ValueError(msg)


def delete_lb_pool(session, pool_id):
    '''
    Deletes a load balancer pool
    '''
    logger.warn('Deleting load balancer %s' % pool_id)
    session.delete_pool(pool_id)


def list_vips(session, vip_id=None):
    '''
    Returns a list of vips or a vip with the id set it vip_id
    '''
    if vip_id is None:
        vips = session.list_vips()
        return vips['vips']
    else:
        vip_filter = filter(lambda vip: vip['id'] == vip_id, list_vips(session))
        return vip_filter[0]


def create_vip(session, name, pool_id, subnet_id, protocol='HTTP', protocol_port='80'):
    '''
    Creates a load balancer vip
    '''
    logger.info('Creating vip %s' % name)
    vip_body = {'vip': {
            'admin_state_up': True,
            'name': name,
            'pool_id': pool_id,
            'protocol': protocol,
            'protocol_port': protocol_port,
            'subnet_id': subnet_id}
    }

    vip = session.create_vip(body=vip_body)

    if vip:
        logger.info('Vip %s created sucessfully!' % name)
        return vip['vip']
    else:
        msg = 'Could not create vip %s' % name
        logger.fatal(msg)
        raise ValueError(msg)


def delete_vip(session, vip_id):
    '''
    Deletes a load balancer vip
    '''
    logger.warn('Deleting vip %s' % vip_id)
    session.delete_vip(vip_id)


def associate_vip_floating_ip(session, floating_ip_id, port_id):
    '''
    Associates a vip with a floating ip address
    '''
    logger.info('Associating vip floating ip %s with port %s' % (floating_ip_id, port_id))
    body = {'floatingip': {
        'port_id': port_id}
    }
    floatingip = session.update_floatingip(floating_ip_id, body=body)

    if floatingip:
        logger.info('Sucessfully associated vip and floating ip %s' % floatingip)
        try:
            nova_client = credentials.get_nova_session()
            return nova.list_floating_ips(nova_client, floating_ip_id=floating_ip_id)
        except Exception, e:
            logger.error(str(e))
            raise e
    else:
        msg = 'Could not associate vip floating ip %s with port %s' % (floating_ip_id, port_id)
        logger.fatal(msg)
        raise ValueError(msg)


def disassociate_vip_floating_ip(session, floating_ip_id):
    '''
    Disassociates a vip from a floating ip
    '''
    logger.info('Removing vip from floating ip %s' % floating_ip_id)
    body = {'floatingip': {
        'port_id': None}
    }
    floatingip = session.update_floatingip(floating_ip_id, body=body)

    if floatingip:
        logger.info('Sucessfully removed vip from floating ip %s' % floating_ip_id)
        try:
            nova_client = credentials.get_nova_session()
            return nova.list_floating_ips(nova_client, floating_ip_id=floating_ip_id)
        except Exception, e:
            logger.error(str(e))
            raise e

    else:
        msg = 'Could not remove vip from floating ip %s' % (floating_ip_id)
        logger.fatal(msg)
        raise ValueError(msg)


def create_lb_pool_member(session, pool_id, address, protocol_port='80'):
    '''
    Adds a server to a load balancer pool
    '''
    logger.info('Creating load balancer pool member for pool %s using ip %s' % (pool_id, address))
    body = {'member': {
        'address': str(address), 
        'protocol_port': str(protocol_port), 
        'pool_id': str(pool_id)}
    }

    lb_member = session.create_member(body=body)

    if lb_member:
        logger.info('Sucessfully created load balancer member %s' % lb_member)
        return lb_member['member']
    else:
        msg = 'Could not create load balancer member for pool %s' % pool_id
        logger.fatal(msg)
        raise ValueError(msg)


def delete_lb_pool_member(session, member_id):
    '''
    Removes a server from a load balancer pool
    '''
    logger.warn('Deleting load balancer member %s' % member_id)
    session.delete_member(member_id)


def create_lb_health_monitor(session, delay, max_retries, timeout, type_, http_method='GET', url_path=None, expected_codes=None):
    '''
    Creates a health monitor for load balancers
    http_method, url_path & expected_codes only required if the type_ is HTTP / HTTPS
    '''
    if type_ is 'PING' or type_ is 'TCP':
        body =  {'health_monitor': {
        'admin_state_up': True,
        'delay': delay,
        'max_retries': max_retries,
        'timeout': timeout,
        'type': type_}
        }
    elif type_ is 'HTTP' or type_ is 'HTTPS':
        if url_path is None or expected_codes is None:
            msg = 'url_path and expected_codes is required for type %s' % type_
            logger.fatal(msg)
            raise ValueError(msg)
        
        body =  {'health_monitor': {
        'admin_state_up': True,
        'delay': delay,
        'max_retries': max_retries,
        'timeout': timeout,
        'http_method': http_method,
        'url_path': url_path,
        'expected_codes': expected_codes,
        'type': type_}
        }
    else:
        msg = 'type_ must be PING, TCP, HTTP or HTTPS'
        logger.error(msg)
        raise ValueError(msg)

    logger.info('Creating new load balancer health monitor with type %s' % type_)
    monitor = session.create_health_monitor(body=body)    
    if monitor:
        logger.info('Sucessfully created load balancer health monitor %s' % monitor)
        return monitor['health_monitor']
    else:
        msg = 'Could not create load balancer health monitor'
        logger.fatal(msg)
        raise ValueError(msg)


def delete_lb_health_monitor(session, health_monitor_id):
    '''
    Deletes a load balancer health monitor
    '''
    logger.warn('Deleting load balancer health monitor %s' % health_monitor_id)
    session.delete_health_monitor(health_monitor_id)


def associate_lb_health_monitor(session, pool_id, health_monitor_id):
    '''
    Associates a health monitor with a load balancer
    '''
    logger.info('Associating load balancer health monitor %s with pool %s' % (health_monitor_id, pool_id))
    body = {'health_monitor': {
            'id': health_monitor_id}
    }
    session.associate_health_monitor(pool_id, body=body)
    return True


def disassociate_lb_health_monitor(session, pool_id, health_monitor_id):
    '''
    Disassociates a health monitor and load balancer
    '''
    logger.info('Disassociating load balancer health monitor %s with pool %s' % (health_monitor_id, pool_id))
    session.disassociate_health_monitor(pool=pool_id, health_monitor=health_monitor_id)
    
