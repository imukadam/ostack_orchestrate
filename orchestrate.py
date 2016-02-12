#!/usr/local/bin/python2.7

import applogger
import credentials
import os
import sys

from config import GW_NET
from config import IMAGE_URL
from config import KEY_NAME
from config import NET_NAME
from config import SUBNET
from config import elk_flavours

import glance
import neutron
import nova

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
        network = neutron.create_network(login, NET_NAME, SUBNET)
        rtr_name = "%s_rtr_%s" % (NET_NAME, login['region_name'])
        router = neutron.set_router(login, rtr_name, NET_NAME, GW_NET)
        logger.info('created rtr %s' % router)
        glance_client = credentials.get_glance_session()
        logger.info('Checking if image %s exists' % os.path.basename(IMAGE_URL))
        req_img = glance.get_images(session=glance_client, img_name=os.path.basename(IMAGE_URL))
        if not req_img:
            logger.info('Image %s does not exist. Need to upload it' % os.path.basename(IMAGE_URL))
            glance.create_image(session=glance_client, img_url=IMAGE_URL)
            # TODO: Need some sort of check to see if image is ready to use
            if glance.wait_for_img(session=glance_client, img_name=os.path.basename(IMAGE_URL)):
                logger.info('Image ready to use')
            else:
                logger.fatal('Image creation NameError')
                raise NameError('Image creation took too long')
        else:
            logger.info('Found image %s' % os.path.basename(IMAGE_URL))
        for componet, componet_flavour in elk_flavours.iteritems():
            logger.info('Attempting to create instance of "%s" in network %s' % (componet, network['id']))
            server_name = ('%s_%s' % (componet, login['region_name']))
            nova_client = credentials.get_nova_sessions(region=login['region_name'])
            my_server = nova.create_server(session=nova_client, srv_name=server_name, key=KEY_NAME, net_uuid=network['id'], flavour=componet_flavour)
            logger.info('Server %s (%s) created' % (my_server.name, my_server.id))

    logger.info('End of %s' % os.path.basename(__file__))


def clean_up():
    logger.info("Cleaning up...")
    auths = credentials.get_auths()
    for login in auths:
        # delete network
        for server in nova.get_servers(credentials.get_nova_sessions(login['region_name']), net_name=NET_NAME):
            nova.delete_server(server)

        server = None

        if len(neutron.list_networks(login, NET_NAME)) > 0:
            neutron.delete_network(login, NET_NAME)


if __name__ == '__main__':
    # Create infrastructure
    main()

    # Remove infrastructure
    # clean_up()
