__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from common import cspace # we use the config file reading function

from os import path
import urllib2
import time
import logging

config = cspace.getConfig(path.dirname(__file__), 'imageserver')
username = config.get('connect', 'username')
password = config.get('connect', 'password')
hostname = config.get('connect', 'hostname')
realm = config.get('connect', 'realm')
protocol = config.get('connect', 'protocol')
port = config.get('connect', 'port')
port = ':%s' % port if port else ''

server = protocol + "://" + hostname + port
passman = urllib2.HTTPPasswordMgr()
passman.add_password(realm, server, username, password)
authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('imageserver startup', '-', '%s' % server))

#@login_required()
def get_image(request, image):
    try:
        url = "%s/cspace-services/%s" % (server, image)
        elapsedtime = time.time()
        f = urllib2.urlopen(url)
        data = f.read()
        elapsedtime = time.time() - elapsedtime
    except urllib2.HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print e.headers
        print 'has WWW-Authenticate', e.headers.has_key('WWW-Authenticate')
        raise
    except urllib2.URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        raise

    logger.info('%s :: %s :: %s' % ('image', '-', '%s :: %8.3f seconds' % (image, elapsedtime)))
    return HttpResponse(data, mimetype='image/jpeg')
