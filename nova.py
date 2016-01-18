#!/usr/local/bin/python2.7

import applogger
import config
import os
import sys

# from novaclient import client

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))


def get_servers(session):
    return session.servers.list()


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
    logger.debug('looking for flavour named %s' % name)
    for img in session.flavors.list():
        if img.name == name:
            return img

    logger.fatal('Could not find flavour named %s' % name)
    raise ValueError('Could not find flavour named %s' % name)


def create_server(session, srv_name, net_uuid, flavour=None):
    if not flavour:
        flavour = "m1.small"
    server = session.servers.create(name=srv_name,
                           image=set_img(session, config.IMAGE),
                           flavor=set_flav(session, flavour),
                           availability_zone="AZ3",
                           nics=[{'net-id': net_uuid}])

    return server


def delete_server(session, srv_name):
    pass
