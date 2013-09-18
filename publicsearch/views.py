__author__ = 'jblowe, amywieliczka'

import os
import re
import time, datetime
import csv
import solr
import cgi
from os import path

from django.contrib.auth.decorators import login_required
from cspace_django_site.settings import STATIC_URL
from cspace_django_site.settings import MEDIA_URL
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.utils.encoding import smart_unicode

from operator import itemgetter
from urllib import urlencode, quote, unquote

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

from cspace_django_site.main import cspace_django_site

# global variables (at least to this module...)
config = cspace_django_site.getConfig()

MAXMARKERS = 65
MAXRESULTS = 1000
MAXLONGRESULTS = 50
#IMAGESERVER = 'http://ucjeps.cspace.berkeley.edu:8180/cspace-services' # no final slash
IMAGESERVER = 'http://localhost:8000/imageserver'
BMAPPERSERVER = 'http://havrc.cspace.berkeley.edu' # no final slash
BMAPPERDIR = 'bmapper'
#BMAPPERTABFILEDIR = '%s/%s/%s' % (BMAPPERSERVER, MEDIA_URL, 'publicsearch/bmapper')
BMAPPERCONFIGFILE = 'ucjeps.xml'
#BMAPPERCONFIGFILEDIR = '%s/%s/%s' % (BMAPPERSERVER, STATIC_URL, 'publicsearch/bmapper-config')
SOLRSERVER = 'http://localhost:8983/solr'
#SOLRCORE = 'ucjeps-metadata'
SOLRCORE = 'ucjeps-metadata'
#LOCALDIR = "/var/www/html/bmapper"  # no final slash
LOCALDIR = '.'

PARMS = {
    # this first one is special
    'keyword': ['Keyword', 'true', 'a keyword search value, please', 'text', ''],

    # the rest are mapping the solr field names to django form labels and fields
    'csid': ['id', 'true', '', 'id', ''],
    'accession': ['Specimen ID', 'true', '', 'accessionnumber_txt', ''],
    'determination': ['Determination', 'true', '', 'determination_txt', ''],
    'majorgroup': ['Major Group', 'true', '', 'majorgroup_txt', ''],
    'collector': ['Collector', 'true', '', 'collector_txt', ''],
    'collectionnumber': ['Collection Number', 'true', '', 'collectornumber_txt', ''],
    'collectiondate': ['Collection Date', 'true', '', 'collectiondate_txt', ''],
    'earlycollectiondate': ['earlycollectiondate_dt', 'true', '', 'earlycollectiondate_dt', ''],
    'latecollectiondate': ['latecollectiondate', 'true', '', 'latecollectiondate_txt', ''],
    'locality': ['Locality', 'true', '', 'locality_txt', ''],
    'county': ['County', 'true', '', 'collcounty_txt', ''],
    'state': ['State', 'true', '', 'collstate_txt', ''],
    'country': ['Country', 'true', '', 'collcountry_txt', ''],
    'elevation': ['Elevation', 'true', '', 'elevation_txt', ''],
    'minelevation': ['Min elevation', 'true', '', 'minelevation_f', ''],
    'maxelevation': ['Max elevation', 'true', '', 'maxelevation_f', ''],
    'elevationunit': ['Elevation unit', 'true', '', 'elevationunit_txt', ''],
    'habitat': ['Habitat', 'true', '', 'habitat_txt', ''],
    'L1': ['L1', 'true', '', 'location_0_coordinate', ''],
    'L2': ['L2', 'true', '', 'location_1_coordinate', ''],
    'trscoordinates': ['TRS coordinates', 'true', '', 'trscoordinates_txt', ''],
    'datum': ['Datum', 'true', '', 'datum_txt', ''],
    'coordinatesource': ['Coordinate source', 'true', '', 'coordinatesource_txt', ''],
    'coordinateuncertainty': ['Coordinate uncertainty', 'true', '', 'coordinateuncertainty_f', ''],
    'coordinateuncertaintyunit': ['Coordinate uncertainty unit', 'true', '', 'coordinateuncertaintyunit_txt', ''],
    'blobs': ['blob_ss', 'true', '', 'blob_ss', ''],
}


def deURN(urn):
    #find identifier in URN
    m = re.search("\'(.*)\'$", urn)
    if m is not None:
        # strip out single quotes
        return m.group(0)[1:len(m.group(0)) - 1]


def getfields(fieldset):
    # for solr faceting
    if fieldset == 'bmapperheader':
        return ["Institution Code",
                "Catalog Number",
                "Scientific Name",
                "Collector",
                "Collector Num Prefix",
                "Collector Num",
                "Collector Num Suffix",
                "early J date",
                "late J date",
                "Date Collected",
                "County",
                "Elevation",
                "Locality",
                "Latitude",
                "Longitude",
                "Datum"]
    elif fieldset == 'bmapperdata':
        return ["na", "accession", "determination", "collector", "na", "collectionnumber", "na", "collectiondate",
                "", "", "county", "elevation", "locality", "L1", "L2", "datum"]
    elif fieldset == 'csvdata':
        return ["ucjeps", "accession", "determination", "collector", "", "collectionnumber", "", "collectiondate",
                "", "", "county", "elevation", "locality", "L1", "L2", "datum"]
    elif fieldset == 'facetfields':
        return ['determination_s', 'majorgroup_s', 'collector_s', 'collcounty_s', 'collstate_s', 'collcountry_s']


def getfacets(response):
    #facets = response.get('facet_counts').get('facet_fields')
    facets = response.facet_counts
    facets = facets['facet_fields']
    _facets = {}
    for key, values in facets.items():
        _v = []
        for k, v in values.items():
            _v.append((k, v))
        _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
    return _facets

def parseTerm(queryterm):
    queryterm = queryterm.strip(' ')
    terms = queryterm.split(' ')
    terms = ['"' + t + '"' for t in terms]
    result = ' AND '.join(terms)
    if 'AND' in result: result = '(' + result + ')' # we only need to wrap the query if it has multiple terms
    return result

def makeMarker(result):
    if 'L1' in result and 'L2' in result:
        #return 'color:green%%7Clabel:G%%7C%s,%s' % (result['L1'], result['L2'])
        #return 'label:%s%%7C%s,%s' % (result['accession'],result['L1'], result['L2'])
        return '%s,%s' % (result['L1'], result['L2'])
    else:
        return None

def writeCsv(filehandle,items,writeheader):

    fieldset = getfields('csvdata')
    writer = csv.writer(filehandle,delimiter='\t')
    # write the berkeley mapper header as the header for the csv file, if asked...
    if writeheader:
        writer.writerow(getfields('bmapperheader'))
    for item in items:
        # get the cells from the item dict in the order specified; make empty cells if key is not found.
        row = []
        for x in fieldset:
            if x in item.keys():
                cell = item[x]
            else:
                cell = ''
            # the following few lines is a hack to handle non-unicode data which appears to be present in the solr datasource
            if isinstance(cell,unicode):
                try:
                    cell = cell.translate({0xd7 : u"x"})
                    cell = cell.decode('utf-8','ignore').encode('utf-8')
                    #cell = cell.decode('utf-8','ignore').encode('utf-8')
                    #cell = cell.decode('utf-8').encode('utf-8')
                except:
                    print 'unicode problem',cell.encode('utf-8','ignore')
                    cell = u'invalid unicode data'
            row.append(cell)
        writer.writerow(row)



def doSearch(solr_server, solr_core, context):
    requestObject = context['searchValues']
    elapsedtime = time.time()
    if 'reset' in requestObject:
        context = {}
    else:
        # create a connection to a solr server
        s = solr.SolrConnection(url='%s/%s' % (solr_server, solr_core))
        queryterms = []
        urlterms = []
        if 'map-google' in requestObject or 'csv' in requestObject:
            querystring = requestObject['querystring']
        else:
            for p in requestObject:
                if p in ['csrfmiddlewaretoken', 'displayType', 'resultsOnly', 'url', 'querystring', 'pane', 'pixonly']: continue
                if 'select-' in p: continue # select control for map markers
                if not p in requestObject: continue
                if not requestObject[p]: continue
                if 'item-' in p:
                    continue
                searchTerm = requestObject[p]
                terms = searchTerm.split('|')
                ANDs = []
                for t in terms:
                    if t == 'OR': t = '"OR"'
                    if t == 'AND': t = '"AND"'
                    ANDs.append('%s:%s' % (PARMS[p][3], t))
                searchTerm = ' AND '.join(ANDs)
                searchTerm = ' (' + searchTerm + ') '
                queryterms.append(searchTerm)
                urlterms.append('%s=%s' % (p, cgi.escape(requestObject[p])))
            querystring = ' AND '.join(queryterms)
            #print querystring

        if urlterms != []: urlterms.append('displayType=%s' % requestObject['displayType'])
        url = '&'.join(urlterms)
        fqs = {}
        try:
            pixonly = requestObject['pixonly']
            querystring += " AND %s:[* TO *]" % PARMS['blobs'][0]
        except:
            pixonly = None
        fields = getfields('facetfields')
        response = s.query(querystring, facet='true', facet_field=fields, fq=fqs, rows=MAXRESULTS, facet_limit=50,
                           facet_mincount=1)

        facetflds = getfacets(response)
        #if pixonly:
        #    results = [r for r in response.results if 'blob_ss' in r.keys()]
        #else:
        #    results = response.results
        results = response.results

        for i,listItem in enumerate(results):
            item = {}
            item['counter'] = i
            for p in PARMS:
                try:
                    # make all arrays into strings for display
                    if type(listItem[PARMS[p][3]]) == type([]):
                        item[p] = ', '.join(listItem[PARMS[p][3]])
                    else:
                        item[p] = listItem[PARMS[p][3]]
                except:
                    #raise
                    pass
            # the list of blob csids need to remain an array, so restore it from psql result
            #item['blob_ss'] = listItem.get('blob_ss')
            if 'blobs' in item.keys():
                item['blobs'] = item['blobs'].split(',')
            item['marker'] = makeMarker(item)
            context['items'].append(item)

        if requestObject['displayType'] in ['v1','v2', 'grid'] and response._numFound > MAXLONGRESULTS:
            context['recordlimit'] = 'items. (limited to %s for long display)' % MAXLONGRESULTS
            context['items'] = context['items'][:MAXLONGRESULTS]
        if requestObject['displayType'] in ['short'] and response._numFound > MAXRESULTS:
            context['recordlimit'] = 'items. (display limited to %s)' % MAXRESULTS

        context['count'] = response._numFound
        m = {}
        for p in PARMS: m[PARMS[p][3].replace('_txt','_s')] = p
        context['fields'] = [m[f] for f in fields]
        context['facetflds'] = [[m[f],facetflds[f]] for f in fields]
        context['range'] = range(len(fields))
        context['fq'] = fqs
        context['url'] = url
        context['pixonly'] = pixonly
        context['querystring'] = querystring
        context['url'] = url
        try:
            context['pane'] = requestObject['pane']
        except:
            context['pane'] = '0'
        try:
            context['resultsOnly'] = requestObject['resultsOnly']
        except:
            pass

    context['core'] = solr_core
    context['time'] = '%8.3f' % (time.time() - elapsedtime)
    return context

#@login_required()
def publicsearch(request):

    if request.method == 'GET':
        requestObject = request.GET
    elif request.method == 'POST':
        requestObject = request.POST
    else:
        pass
        #error!

    context = {'items': [], 'searchValues': requestObject}
    if requestObject != {}:
        form = forms.Form(requestObject)

        if form.is_valid() or request.method == 'GET':
            context = doSearch(SOLRSERVER, SOLRCORE, context)
            if 'search' in requestObject:
                pass
            elif 'csv' in requestObject:

                # Create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="ucjeps.csv"'

                #response.write(u'\ufeff'.encode('utf8'))
                writeCsv(response,context['items'],writeheader=True)
                return response

            elif 'map-bmapper' in requestObject:
                context['berkeleymapper'] = 'set'
                context['url'] = requestObject['url']
                mappableitems = []
                for item in context['items']:
                    m = makeMarker(item)
                    if m is not None:
                        mappableitems.append(item)
                context['mapmsg'] = []
                filename = 'bmapper%s.csv' % datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                #filehandle = open(filename, 'wb')
                filehandle = open(path.join(LOCALDIR,filename), 'wb')
                writeCsv(filehandle,mappableitems,writeheader=False)
                filehandle.close()
                context['mapmsg'].append('%s points of the %s selected objects examined had latlongs (%s in result set).' % (len(mappableitems), len(context['items']),context['count']))
                #context['mapmsg'].append('if our connection to berkeley mapper were working, you be able see them plotted there.')
                context['items'] = mappableitems
                bmapperconfigfile = '%s/%s/%s' % (BMAPPERSERVER,BMAPPERDIR,BMAPPERCONFIGFILE)
                tabfile = '%s/%s/%s' % (BMAPPERSERVER,BMAPPERDIR,filename)
                context['bmapperurl'] = "http://berkeleymapper.berkeley.edu/run.php?ViewResults=tab&tabfile=%s&configfile=%s&sourcename=Consortium+of+California+Herbaria+result+set&maptype=Terrain" % (tabfile,bmapperconfigfile)
                return HttpResponseRedirect(context['bmapperurl'])

            elif 'map-google' in requestObject:
                context['url'] = requestObject['url']
                selected = []
                for p in requestObject:
                    if 'item-' in p:
                        selected.append(requestObject[p])
                mappableitems = []
                markerlist = []
                for item in context['items']:
                    if item['csid'] in selected:
                        m = makeMarker(item)
                        if len(mappableitems) >= MAXMARKERS: break
                        if m is not None:
                            #print 'm= x%sx' % m
                            markerlist.append(m)
                            mappableitems.append(item)
                context['mapmsg'] = []
                if len(context['items']) < context['count']:
                    context['mapmsg'].append('%s points plotted. %s selected objects examined (of %s in result set).' % (len(markerlist), len(context['items']),context['count']))
                else:
                    context['mapmsg'].append('%s points plotted. all %s selected objects in result set examined.' % (len(markerlist), context['count']))
                context['items'] = mappableitems
                context['markerlist'] = '&markers='.join(markerlist[:MAXMARKERS])
                if len(markerlist) >= MAXMARKERS:
                    context['mapmsg'].append('%s points is the limit. Only first %s accessions (with latlongs) plotted!' % (MAXMARKERS,len(markerlist)))
            elif 'email' in requestObject:
                pass

    context['imageserver'] = IMAGESERVER
    if 'displayType' in requestObject:
        context['displayType'] = requestObject['displayType']
    else:
        context['displayType'] = 'short'

    context['displayTypes'] = (
        ('short', 'Short'),
        ('v1', 'v1'),
        ('v2', 'v2'),
        ('grid', 'Grid'),
    )

    return render(request, 'publicsearch.html', context)