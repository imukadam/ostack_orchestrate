#!/usr/local/bin/python2.7

import applogger
import credentials
import os
import sys

from config import NET_NAME
from config import SUBNET
from config import elk_flavours

from neutron import create_network
from neutron import delete_network
from nova import create_server

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

    # for login in auths:
    #     logger.info('Attempting to create network "%s" in region %s' % (NET_NAME, login['region_name']))
    #     network = create_network(login, NET_NAME, SUBNET)
    #     for componet, componet_flavour in elk_flavours.iteritems():
    #         logger.info('Attempting to create instance of "%s" in network %s' % (componet, network['id']))
    #         server_name = ('%s_%s' % (componet, login['region_name']))
    #         nova_client = credentials.get_nova_sessions(region=login['region_name'])
    #         my_server = create_server(session=nova_client, srv_name=server_name, net_uuid=network['id'], flavour=componet_flavour)
    #         logger.info('Server %s created with IP %s' % (my_server.name, my_server.networks[network['name']]))

    clean_up()
    logger.info('End of %s' % os.path.basename(__file__))


def clean_up():
    logger.info("Cleaning up...")
    auths = credentials.get_auths()
    for login in auths:
        #delete network
        delete_network(login, NET_NAME)


if __name__ == '__main__':
    main()

    # nova_client = credentials.get_nova_sessions()
    # print(nova_client)
    # flav = set_flav(nova_client, 'm1.small')
    # print(type(flav))

    # for key, value in config.elk_flavours.iteritems():
    #     print(key)
