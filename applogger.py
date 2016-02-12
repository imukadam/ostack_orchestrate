#!/usr/local/bin/python2.7

# import ConfigParser
import config
import logging
# import os

CFG_FILE = config.CFG_FILE
# CONFIG = ConfigParser.ConfigParser()
# CONFIG.read(CFG_FILE)

ENV = config.ENV
LOG_FILE = config.LOG_FILE
LOG_LEVEL = config.LOG_LEVEL


def setLogger():
    '''
    Set
    '''
    console_set = False
    if len(logging.getLogger().handlers) == 0:
        if LOG_LEVEL == 'DEBUG':
            logging.basicConfig(filename=LOG_FILE, format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %X %Z', level=logging.DEBUG)
        else:
            logging.basicConfig(filename=LOG_FILE, format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %X %Z', level=logging.INFO)
        if ENV == 'DEV':
            for h in logging.getLogger().handlers:
                if type(h) is logging.StreamHandler:
                    console_set = True
            if not console_set:
                console = logging.StreamHandler()
                console.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)s - %(message)s')
                console.setFormatter(fmt=formatter)
                logging.getLogger().addHandler(console)
    return logging


def chkLogger():
    return len(logging.getLogger().handlers)


def getLogger():
    return logging.getLogger()
