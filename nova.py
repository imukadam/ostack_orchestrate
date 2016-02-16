#!/usr/local/bin/python2.7

import applogger
import os
import sys

import config

from os.path import basename
from time import sleep

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))


def get_servers(session, srv_name=None, net_name=None):
    if srv_name is None and net_name is None:
        return session.servers.list()
    else:
        if net_name is not None and srv_name is None:
            net_filter = filter(lambda servers: servers.networks.keys()[0] == net_name, get_servers(session))
            return net_filter

        srv_filter = filter(lambda servers: servers.name == srv_name, get_servers(session, net_name=net_name))
        return srv_filter


def set_flav(session, name):
    '''
    Returns flavour object
    '''
    logger.debug('looking for flavour named %s' % name)
    for flavour in session.flavors.list():
        if flavour.name == name:
            return flavour

    logger.fatal('Could not find flavour named %s' % name)
    raise ValueError('Could not find flavour named %s' % name)


def set_img(session, name):
    '''
    Returns image object
    '''
    logger.debug('looking for images named %s' % name)
    for img in session.images.list():
        if img.name == name:
            return img

    logger.warn('Could not find image named %s' % name)
    return None


def list_keys(session, key_name):
    '''
    Returns the key object for a given key name else None.
    '''
    for key in session.keypairs.list():
        if key.name == key_name:
            return key

    return None


def list_availability_zones(session, zone_name):
    for zone in session.availability_zones.list(detailed=False):
        if zone.zoneName == zone_name:
            return zone

    return None


def create_server(session, srv_name, net_uuid, az=None, key=None, flavour=None):
    if not flavour:
        flavour = "m1.small"
    if key:
        # Check if key exists
        if not list_keys(session, key):
            msg = 'Could not find key named %s' % key
            logger.fatal(msg)
            raise ValueError(msg)
        else:
            logger.info('Found key %s' % key)

    if az:
        zone = list_availability_zones(session=session, zone_name=az)
        if not zone:
            msg = 'Could not find AZ named %s' % az
            logger.fatal(msg)
            raise ValueError(msg)

    image = set_img(session, basename(config.IMAGE_URL))
    if image:
        server = session.servers.create(name=srv_name,
                                        image=image,
                                        flavor=set_flav(session, flavour),
                                        key_name=key,
                                        nics=[{'net-id': net_uuid}])
    else:
        msg = 'Could not find image named %s' % basename(config.IMAGE_URL)
        logger.fatal(msg)
        raise ValueError(msg)

    return server


def delete_server(server):
    logger.warn("Deleting server %s" % server.name)
    server.delete()
    sleep(5)  # Pause as the remove takes a bit of time to register


def create_floating_ip(session, network):
    '''
    Creates a floating ip from the given network
    '''
    floating_ip = session.floating_ips.create(network)
    if floating_ip:
        logger.info("Allocated floating IP %s for %s network." % (floating_ip.ip, network))
    else:
        msg = "Could not allocate floating IP for %s network. Check taht you have enough quota." % network
        logger.fatal(msg)
        raise ValueError(msg)

    return floating_ip


def delete_floating_ip(floating_ip):
    '''
    Deletes a floating ip
    '''
    logger.warn("Deleting floating ip %s" % floating_ip.ip)
    floating_ip.delete()


def associate_floating_ip(session, server, floating_ip):
    '''
    Associates a floating ip with a server. Returns the floating ip object with the instance added.
    '''
    session.servers.add_floating_ip(server=server, address=floating_ip)
    floating_ip = session.floating_ips.get(floating_ip)
    # Check IP has been associated
    if floating_ip.instance_id == server.id:
        logger.info("Floating ip %s has been added to server %s (%s)" % (floating_ip.ip, server.name, server.id))
    else:
        msg = "Failed to associate floating ip %s with server %s (%s)" % (floating_ip.ip, server.name, server.id)
        logger.fatal(msg)
        raise ValueError(msg)

    return floating_ip


def disassociate_floating_ip(session, server, floating_ip):
    '''
    Disassociates a server and floating ip. Returns the floating ip object with the instance removed.
    '''
    logger.info("Removing %s from instance %s" % (floating_ip.ip, floating_ip.instance_id))
    if floating_ip.instance_id != server.id:
        msg = "Floating ip %s has not been associated to server %s" % (floating_ip.ip, server)
        logger.fatal(msg)
        raise ValueError(msg)
    else:
        session.servers.remove_floating_ip(server=server, address=floating_ip)

    return floating_ip


def list_floating_ips(session, server_id=None):
    '''
    Returns a list of floating ips for a server or a list of all floating ips
    '''
    if server_id is None:
        return session.floating_ips.list()
    else:
        srv_filter = []
        for floating_ip in list_floating_ips(session):
            if floating_ip.instance_id == server_id:
                srv_filter.append(floating_ip)
        return srv_filter
