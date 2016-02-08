#!/usr/local/bin/python2.7

import ConfigParser
import os

CFG_FILE = os.path.dirname(__file__) + '/config.cfg'
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(CFG_FILE)

ENV = CONFIG.get('ENV', 'ENV')
LOG_FILE = CONFIG.get(ENV, 'LOG_FILE')

USERNAME = CONFIG.get(ENV, 'USERNAME')
PASSWORD = CONFIG.get(ENV, 'PASSWORD')
AUTH_URL = CONFIG.get(ENV, 'AUTH_URL')
TENANT_NAME = CONFIG.get(ENV, 'TENANT_NAME')
PROJECT_ID = CONFIG.get(ENV, 'PROJECT_ID')
REGIONS = CONFIG.get(ENV, 'REGIONS')

NET_NAME = CONFIG.get(ENV, "NET_NAME")
SUBNET = CONFIG.get(ENV, "SUBNET")
GW_NET = CONFIG.get(ENV, "GW_NET")

IMAGE_URL = CONFIG.get(ENV, "IMAGE_URL")
KEY_NAME =  CONFIG.get(ENV, "KEY_NAME")
elk_flavours = {
    'elasticsearch': CONFIG.get(ENV, "ES_FLAV"),
    'logstash': CONFIG.get(ENV, "LS_FLAV"),
    'kibana': CONFIG.get(ENV, "KIB_FLAV")
}
