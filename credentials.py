#!/usr/local/bin/python2.7

# import ConfigParser
import applogger
import config
import os
import sys

from novaclient import client

# Set encoding type to UTF8
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


def get_auths():
    '''
    Returns a list of dict that contain log in information for openstack
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


def get_nova_sessions(region):
    '''
    Returns a nova client connection to selected region
    '''
    auth_details = get_auths()
    nova_session = client.Client('2',
                                 auth_details[0]['username'],
                                 auth_details[0]['password'],
                                 auth_details[0]['tenant_name'],
                                 auth_details[0]['auth_url'],
                                 region_name=region,
                                 connection_pool=True)

    return nova_session


# def main():
#     a = get_nova_sessions()
#     print(a)


# if __name__ == '__main__':
#     main()
