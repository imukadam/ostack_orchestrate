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


def get_images(session, img_name=None):
    '''
    Retuns all images in given tenacy or images matching img_name
    '''
    if img_name is None:
        return list(session.images.list())
    else:
        img_filter = filter(lambda image: image['name'] == img_name, get_images(session))
        if len(img_filter) == 0:
            return None

        return img_filter


def wait_for_img(session, img_name, timeout=300, refresh=1.0):
    '''
    Return True if image is ready to use within a given time else return False
    '''
    endtime = time.time() + timeout
    while time.time() < endtime:
        time.sleep(refresh)
        logger.info('Checking if image %s ready' % img_name)
        try:
            img = get_images(session=session, img_name=img_name)
            if img:
                print(img[0])
                if img[0]['status'] == 'active':
                    logger.info('Yay! Image %s ready to use' % img_name)
                    return True
        except Exception as e:
            logger.error('Got error %s' % str(e))
            return e

    raise ValueError('Timeout expired before image was ready. Maybe consider increasing timeout vlaue to higher then %f sec?' % timeout)


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
    logger.info('Uploding %s' % img_url)
    try:
        session.tasks.create(type='import', input=body)
    except Exception as e:
        logger.warn('Got the error %s...ask LSD team about this' % str(e))
