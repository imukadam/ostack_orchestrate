#!/usr/local/bin/python2.7

import applogger
import os
import sys

# Set encoding type to UTF8
reload(sys)
sys.setdefaultencoding('UTF8')

if applogger.chkLogger() > 0:
    logger = applogger.getLogger()
else:
    logger = applogger.setLogger()
logger.debug(msg='Running %s' % os.path.basename(__file__))

def get_images(session, img_name=None):
    '''
    Retuns all images in given tenacy or images matching img_name
    '''
    if img_name is None:
        return list(session.images.list())
    else:
        img_filter = filter(lambda image: image['name'] == img_name, get_images(session))
        return img_filter


def create_image(session, img_url):
    '''
    Creates an image in the given tenancy
    '''

    img_props = {
        "name": os.path.basename(img_url),
        "disk_format": os.path.splitext(img_url)[-1],
        "container_format": "bare"
    }

    body = {
        'import_from': img_url,
        "import_from_format": os.path.splitext(img_url)[-1],
        "image_properties": img_props
    }
    print(body)
    try:
        session.tasks.create(type='import', input=body)
    except Exception as e:
        logger.warn('Got the error %s...ask LSD team about this' % str(e))
