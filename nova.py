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


def create_server(session, srv_name, net_uuid, key=None, flavour=None):
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
