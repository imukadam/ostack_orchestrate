#!/usr/local/bin/python2.7

import applogger
import os
import sys
import time

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))

def list_volumes(session, vol_id=None, server_id=None):
    '''
    Retuns volumes in given tenacy, volumes attached to a server or volumes matching vol_id
    '''
    if vol_id is None and server_id is None:
        return session.volumes.list()
    elif server_id:
        srv_filter = []
        for volume in list_volumes(session):
            if len(volume.attachments) > 0:
                if volume.attachments[0]['server_id'] == server_id:
                    srv_filter.append(volume)
        return srv_filter
    else:
        vol_filter = filter(lambda volume: volume.id == vol_id, list_volumes(session))
        if len(vol_filter) == 0:
            return None

        return vol_filter

def create_volume(session, display_name, availability_zone, size=5):
    '''
    Creates a new volume. Reterns volume object.
    '''
    logger.info("Creating volume %s" % display_name)
    vol = session.volumes.create(display_name=display_name, availability_zone=availability_zone, size=size)
    if vol:
        logger.info("Volume %s (%s) has successfully been created" % (display_name, vol.id))
    else:
        msg = "Creating volume %s failed." % display_name
        logger.fatal(msg)
        raise ValueError(msg)
    time.sleep(5) # Wait for volume to create
    return vol

def delete_volume(volume):
    '''
    Deletes a volume
    '''
    logger.warn("Deleting volume %s (%s)" % (volume.name, volume.id))
    volume.delete()
