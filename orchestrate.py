#!/usr/local/bin/python2.7

import applogger
import credentials
import os
import sys
import time

from config import NET_NAME
from config import SUBNET
from config import elk_flavours

from neutron import create_network
from neutron import delete_network
from neutron import list_networks
from nova import create_server
from nova import delete_server
from nova import get_servers

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))


def main():
    '''
    main py block
    '''
    logger.info("Starting up %s" % os.path.basename(__file__))
    auths = credentials.get_auths()

    for login in auths:
        logger.info('Attempting to create network "%s" in region %s' % (NET_NAME, login['region_name']))
        network = create_network(login, NET_NAME, SUBNET)
        for componet, componet_flavour in elk_flavours.iteritems():
            logger.info('Attempting to create instance of "%s" in network %s' % (componet, network['id']))
            server_name = ('%s_%s' % (componet, login['region_name']))
            nova_client = credentials.get_nova_sessions(region=login['region_name'])
            my_server = create_server(session=nova_client, srv_name=server_name, net_uuid=network['id'], flavour=componet_flavour)
            logger.info('Server %s (%s) created' % (my_server.name, my_server.id))

    logger.info('End of %s' % os.path.basename(__file__))


def clean_up():
    logger.info("Cleaning up...")
    auths = credentials.get_auths()
    for login in auths:
        #delete network
        for server in get_servers(credentials.get_nova_sessions(login['region_name']), net_name=NET_NAME):
            delete_server(server)

        server = None
        logger.info('Waiting on server deletion cleanup')
        time.sleep(10)

        if len(list_networks(login, NET_NAME)) > 0:
            delete_network(login, NET_NAME)


if __name__ == '__main__':
    # main()
    clean_up()


    # nova_client = credentials.get_nova_sessions()
    # print(nova_client)
