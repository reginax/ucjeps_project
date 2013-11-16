__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from common import cspace
from cspace_django_site.main import cspace_django_site

from os import path
from ConfigParser import NoOptionError
import urllib2
import ConfigParser
import time


#@login_required()
def get_image(request, image):

    realm = 'org.collectionspace.services'
    protocol = 'http'
    port = '8180'

    hostname = 'ucjeps.cspace.berkeley.edu'
    username = 'search@ucjeps.cspace.berkeley.edu'
    password = 'xxxpasswordxxx'
    #password = 'xxxpasswordxxx'

    server = protocol + "://" + hostname + ":" + port
    passman = urllib2.HTTPPasswordMgr()
    passman.add_password(realm, server, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    url = "%s/cspace-services/%s" % (server, image)
    elapsedtime = 0

    try:
        elapsedtime = time.time()
        f = urllib2.urlopen(url)
        data = f.read()
        elapsedtime = time.time() - elapsedtime
    except urllib2.HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        raise
    except urllib2.URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        raise
    else:
        return HttpResponse(data, mimetype='image/jpeg')
