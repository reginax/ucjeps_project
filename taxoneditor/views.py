__author__ = 'jblowe'

import re
import requests
import urllib
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from common.utils import deURN
from taxon import taxon_template

from uploadmedia.cswaExtras import postxml, relationsPayload, getConfig, getCSID
from utils import termTypeDropdowns, termStatusDropdowns, taxonRankDropdowns, taxonfields, labels, formfields, numberWanted
from utils import extractTag, xName, TITLE

# alas, there are many ways the XML parsing functionality might be installed.
# the following code attempts to find and import the best...
try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring

    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree

        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree

            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree

                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")

from common import cspace
from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()

@login_required()
def taxoneditor(request):
    resolutionservice = ''
    formfield = 'determination'

    timestamp = 'timestamp'
    version = 'version'

    if formfield in request.GET:
        kw = request.GET[formfield]
        if 'source' in request.GET:
            sources = request.GET.getlist('source')
        else:
            sources = []
        # do search
        results = {'CollectionSpace': [], 'GBIF': [], 'Tropicos': []}
        Ourid = 0
        # '() NameId Family ScientificNameWithAuthors ScientificName () NameId'
        if 'CSpace' in sources:
            connection = cspace.connection.create_connection(config, request.user)
            print 'cspace-services/taxonomyauthority/87036424-e55f-4e39-bd12/items?pt=%s&wf_deleted=false&pgSz=%s' % (
                urllib.quote_plus(kw), numberWanted)
            (url, data, statusCode) = connection.make_get_request(
                'cspace-services/taxonomyauthority/87036424-e55f-4e39-bd12/items?pt=%s&wf_deleted=false&pgSz=%s' % (
                    urllib.quote_plus(kw), numberWanted))
            # 'cspace-services/%s?kw=%s&wf_deleted=false' % ('taxon', kw))
            # ...collectionobjects?kw=%27orchid%27&wf_deleted=false
            cspaceXML = fromstring(data)
            items = cspaceXML.findall('.//list-item')
            numberofitems = len(items)
            for i in items:
                Ourid += 1
                if Ourid > numberWanted: break
                csid = i.find('.//csid')
                csid = csid.text
                termDisplayName = extractTag(i,'termDisplayName')
                taxonRefname = extractTag(i,'taxon')

                print 'cspace-services/taxonomyauthority/87036424-e55f-4e39-bd12/items/%s' % csid
                (url, taxondata, statusCode) = connection.make_get_request(
                    'cspace-services/taxonomyauthority/87036424-e55f-4e39-bd12/items/%s' % csid)
                taxonXML = fromstring(taxondata)
                family = extractTag(taxonXML, 'family')
                #termDisplayName = extractTag(taxonXML, 'termDisplayName')
                termName = extractTag(taxonXML, 'termName')
                commonName = extractTag(taxonXML, 'commonName')

                r = [Ourid, family, '', termDisplayName, termName, commonName, 'CSpace', csid]
                r = [ ['', x] for x in r]

                # hardcoded here for now, should eventually get these from the authentication backend
                # but tenant is not even stored there...
                #h ostname = 'pahma.cspace.berkeley.edu'
                # tenant = 'pahma'
                # link = 'http://%s/collectionspace/ui/%s/html/cataloging.html?csid=%s' % (hostname, tenant, csid)
                results['CollectionSpace'].append(r)
        if 'Tropicos' in sources:
            resolutionservice = 'Tropicos'
            # do GBIF search
            # params = urllib.urlencode({'name': kw})
            tropicosURL = "http://services.tropicos.org/Name/Search?name=%s&pagesize=%s&apikey=d0a905a9-75c9-466e-bbab-5b568f4e8b91&format=json"
            response = requests.get(tropicosURL % (urllib.quote_plus(kw),numberWanted))
            print tropicosURL % (urllib.quote_plus(kw),numberWanted)
            response.encoding = 'utf-8'
            try:
                names2use = response.json()
                errormsg = 'could not parse returned JSON, or it was empty'
                if 'Error' in names2use[0]:
                    names2use = []
            except:
                names2use = []
            numberofitems = len(names2use)
            if len(names2use) > numberWanted:
                names2use = names2use[:numberWanted]
            for name in names2use:
                Ourid += 1
                r = []
                for i,fieldname in enumerate('X Family X ScientificNameWithAuthors ScientificName CommonName X NameId'.split(' ')):
                    r.append(xName(name, fieldname, i))
                r[0] = ['id', Ourid]
                r[6] = ['termSource', 'Tropicos']
                #r = {'id': Ourid, 'family': name['Family'], 'idsource': 'Tropicos', 'id': name['NameId'],
                #     'scientificnamewithauthors': name['ScientificNameWithAuthors'],
                #     'scientificname': name['ScientificName']}
                results['Tropicos'].append(r)
            pass
        if 'GBIF' in sources:
            resolutionservice = 'GBIF'
            # do Tropicos search
            # params = urllib.urlencode({'name': kw})
            response = requests.get('http://api.gbif.org/v1/species/search', params={'q': kw})
            print 'http://api.gbif.org/v1/parser/name/%s' % urllib.quote_plus(kw)
            response.encoding = 'utf-8'

            names2use = response.json()
            names2use = names2use['results']
            numberofitems = len(names2use)
            if len(names2use) > numberWanted:
                names2use = names2use[:numberWanted]
            for name in names2use:
                if 'accordingTo' in name and 'NUB Generator' in name['accordingTo']:
                    continue
                Ourid += 1
                # get phylum from both?!
                r = []
                for i,fieldname in enumerate('X family family scientificName canonicalName CommonName X taxonID'.split(' ')):
                    r.append(xName(name, fieldname, i))
                r[0] = ['id', Ourid]
                r[6] = ['termSource', 'GBIF']
                results['GBIF'].append(r)
            pass
        return render(request, 'taxoneditor.html', {'timestamp': timestamp, 'version': version, 'fields': formfields,
                                                    'labels': labels, 'results': results, 'taxon': kw,
                                                    'suggestsource': 'solr', 'source': sources,
                                                    'resolutionservice': resolutionservice, 'apptitle': TITLE})

    else:
        return render(request, 'taxoneditor.html', {'timestamp': timestamp, 'version': version,
                                                    'title': TITLE, 'suggestsource': 'solr',
                                                    'resolutionservice': resolutionservice, 'apptitle': TITLE})


def load_payload(payload,request,cspace_fields):
    for field in cspace_fields:
        if field in request:
            payload = payload.replace('{%s}' % field, request[field])

    # get rid of any unsubstituted items in the template
    payload = re.sub(r'\{.*?\}', '', payload)
    #payload = payload.replace('INSTITUTION', institution)
    return payload


@login_required()
def create_taxon(request):

    timestamp = 'timestamp'
    version = 'version'

    payload = load_payload(taxon_template,request,taxonfields)
    uri = 'taxon'

    elapsedtimetotal = time.time()
    messages = []
    messages.append("posting to %s REST API..." % uri)
    # messages.append(payload)
    (url, data, taxonCSID, elapsedtime) = postxml('POST', uri, http_parms.realm, http_parms.hostname, http_parms.username, http_parms.password, payload)
    # elapsedtimetotal += elapsedtime
    messages.append('got csid %s elapsedtime %s ' % (taxonCSID, elapsedtime))
    messages.append("%s REST API post succeeded..." % uri)

    return render(request, 'taxoneditor.html', {'timestamp': timestamp, 'version': version, 'fields': formfields,
                                                'labels': labels, 'messages': messages, 'taxon': '',
                                                'suggestsource': 'solr', 'source': ['Taxa Created'],
                                                'resolutionservice': '', 'apptitle': TITLE})
