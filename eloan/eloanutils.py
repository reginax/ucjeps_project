__author__ = 'rjaffe (after jblowe\'s "imageserver")'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from common import cspace
from cspace_django_site.main import cspace_django_site
from publicsearch.utils import doSearch

from os import path
from ConfigParser import NoOptionError
import urllib2
import ConfigParser
import time
import re


#@login_required()
def get_entity(request, entitytype, responsemimetype):
    """ Connects to CollectionSpace server, makes request to cspace-services RESTful API.


    Returns xml payload or images.

    :param request:
    :param entitytype:
    :param responsemimetype:
    :return:
    """
    #config = cspace_django_site.getConfig()
    #connection = cspace.connection.create_connection(config, request.user)
    #(url, data, statusCode) = connection.make_get_request('cspace-services/%s' % image)
    #return HttpResponse(data, mimetype='image/jpeg')

    realm = 'org.collectionspace.services'
    # uri = 'cspace-services/accounts/0/accountperms'
    protocol = 'http'
    port = '8180'

    hostname = 'ucjeps-dev.cspace.berkeley.edu'
    username = 'admin@ucjeps.cspace.berkeley.edu'
    # TODO xxxxx password value out before committing to github
    password = 'xxxxxx'

    server = protocol + "://" + hostname + ":" + port
    passman = urllib2.HTTPPasswordMgr()
    passman.add_password(realm, server, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    url = "%s/cspace-services/%s" % (server, entitytype)
    #print "<p>%s</p>" % url
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
        #return (url,data,elapsedtime)
        return HttpResponse(data, mimetype=responsemimetype)

def build_solr_query(solr_server, solr_core, solr_queryparam_key, solr_queryparam_value):
    """
    Takes solr query information, searches against ucjeps_project publicsearch portal.


    Returns search results.

    :param solr_server:
    :param solr_core:
    :param solr_queryparam_key:
    :param solr_queryparam_value:
    :return: results:
    """
    query_dictionary = {solr_queryparam_key: solr_queryparam_value, 'displayType': 'full', 'maxresults': '2000'}
    solr_context = {'searchValues': query_dictionary}
    # from publicsearch/utils.py
    results = doSearch(solr_server, solr_core, solr_context)
    return results

def getInstitutionCodefromDisplayName(element,xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    if re.match(r".*:item:name\(.+?\)'.*\).*'$", result):
        result = re.sub(r"^.*:item:name\(.+?\)'.*\((.*)\).*\'$", "\\1", result)
    else:
        result = ''
    return result

def getShortIdfromRefName(element,xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*:item:name\((.+?)\).*\'$", "\\1", result)
    return result
