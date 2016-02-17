#!/usr/local/bin/python2.7

# import ConfigParser
import applogger
import config
import os
import sys

from glanceclient import Client as glance_client
from keystoneclient import session
from keystoneclient.auth.identity import v2
from novaclient import client as nova_client
from cinderclient.v2 import client as cinder_client

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


def get_keystone_sess():
    auth_details = get_auths()
    auth = v2.Password(auth_url=auth_details[0]['auth_url'],
                       username=auth_details[0]['username'],
                       password=auth_details[0]['password'],
                       tenant_id=config.PROJECT_ID)

    ks_session = session.Session(auth=auth)

    return ks_session


def get_nova_sessions(region):
    '''
    Returns a nova client connection to selected region
    '''
    auth_details = get_auths()
    nova_session = nova_client.Client('2',
                                      auth_details[0]['username'],
                                      auth_details[0]['password'],
                                      auth_details[0]['tenant_name'],
                                      auth_details[0]['auth_url'],
                                      region_name=region,
                                      connection_pool=True
                                      )

    return nova_session


def get_glance_session():
    '''
    Returns a glance client connection
    '''
    glance_session = glance_client('2', session=get_keystone_sess())

    return glance_session


def get_cinder_session(region):
    '''
    Returns a cinder client connection
    '''
    auth_details = get_auths()
    cinder_session = cinder_client.Client(auth_details[0]['username'],
                                          auth_details[0]['password'],
                                          auth_details[0]['tenant_name'], 
                                          auth_details[0]['auth_url'],
                                          region_name=region,
                                          service_type="volume"
                                          )
    return cinder_session
