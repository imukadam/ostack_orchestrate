#!/usr/local/bin/python2.7

import sys

from keystoneclient import session
from keystoneclient.auth.identity import v2
from novaclient import client

#Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')
