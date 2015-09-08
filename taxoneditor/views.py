__author__ = 'jblowe'

import re
import requests
import urllib

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from search.utils import deURN

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
TITLE = 'Taxon Editor'
numberWanted = 10

termTypeDropdowns = [('descriptor', 'descriptor'), ('Leave empty', '')]
termStatusDropdowns = [('accepted', 'accepted'), ('Leave empty', '')]
taxonRankDropdowns = [('species', 'species'), ('genus', 'genus')]
taxonfields = [
    ('n', 'N', 'ignore'),
    ('family', 'Family', 'refName'),
    ('taxonMajorGroup', 'Major Group', 'string'),
    ('termDisplayName', 'Scientific Name with Authors', 'string'),
    ('termName', 'Scientific Name', 'string'),
    ('commonName', 'Common Name', 'refName'),
    ('termSource', 'Source', 'string'),
    ('termSourceID', 'Source ID', 'string'),
    # these are constants or derived (i.e. not from service)
    ('termFormattedDisplayName', 'Formatted Scientific Name', 'string'),
    ('taxonomicStatus', 'Taxonomic Status', 'string'),
    ('termPrefForLang', 'Term Language', 'string'),
    ('termType', 'Term Type', 'dropdown', termTypeDropdowns),
    ('termStatus', 'Term Status', 'dropdown', termStatusDropdowns),
    ('taxonCurrency', 'Taxon Currency', 'string'),
    ('inAuthority', 'Authority CSID', 'ignore'),
    ('taxonRank', 'Rank', 'dropdown', taxonRankDropdowns),
]

# labels = 'n,family,major group,scientific name with authors,scientific name,idsource,id'.split(',')
labels = [n[1] for n in taxonfields]
labels = labels[:7]

formfields = [{'name': f[0], 'label': f[1], 'fieldtype': f[2], 'value': '', 'type': 'text'} for f in taxonfields]


def xName(name, fieldname):
    if fieldname in name:
        if name[fieldname] is not None:
            return name[fieldname]
        else:
            return ''
    else:
        return 'not found'


def extractTag(xml, tag):
    element = xml.find('.//%s' % tag)
    try:
        if "urn:" in element.text:
            element_text = deURN(str(element.text))
        else:
            element_text = element.text
    except:
        element_text = ''
    return element_text


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
            tropicosURL = "http://services.tropicos.org/Name/Search?name=%s&type=wildcard&apikey=d0a905a9-75c9-466e-bbab-5b568f4e8b91&format=json"
            response = requests.get(tropicosURL % urllib.quote_plus(kw))
            print tropicosURL % urllib.quote_plus(kw)
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
                for fieldname in 'X Family X ScientificNameWithAuthors ScientificName CommonName X NameId'.split(' '):
                    r.append(xName(name, fieldname))
                r[0] = Ourid
                r[6] = 'Tropicos'
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
                for fieldname in 'X family family scientificName canonicalName CommonName X taxonID'.split(' '):
                    r.append(xName(name, fieldname))
                r[0] = Ourid
                r[6] = 'GBIF'
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
