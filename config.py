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

NET_NAME = CONFIG.get(ENV, "NET_NAME")
SUBNET = CONFIG.get(ENV, "SUBNET")