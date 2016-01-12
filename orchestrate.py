#!/usr/local/bin/python2.7

import applogger
import config
import os
import sys

from neutron import create_network

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))


def main():
    logger.info('Attempting to create network "%s"' % config.NET_NAME)
    net_status = create_network(config.NET_NAME, config.SUBNET)
    if net_status:
        logger.info("Continue")
    else:
        logger.error("fail")
    logger.info('End of %s' % os.path.basename(__file__))


if __name__ == '__main__':
    main()
