#!/usr/local/bin/python2.7

# import ConfigParser
import applogger
import config
import os
import sys

#Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))

CFG_FILE = config.CFG_FILE
# CONFIG = ConfigParser.ConfigParser()
# CONFIG.read(CFG_FILE)

# ENV = CONFIG.get('ENV', 'ENV')


def get_credentials():
    '''
    Returns a list of dict that contain loging informatiion for openstack
    '''
    regions = str(config.REGIONS).split(',')
    regions_auth = []
    for region in regions:
        config_variables = {}
        config_variables['username'] = config.USERNAME
        config_variables['password'] = config.PASSWORD
        config_variables['auth_url'] = config.AUTH_URL
        config_variables['tenant_name'] = config.TENANT_NAME
        config_variables['region_name'] = region
        regions_auth.append(config_variables)

    return regions_auth
