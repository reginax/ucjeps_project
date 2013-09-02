__author__ = 'amywieliczka, jblowe'

import os
import re
import time
import csv
import solr
import cgi

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
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

config = cspace_django_site.getConfig()

parms = {
    # these first two are special
    'keyword': ['orchid', 'true', 'a keyword search value, please', 'text', ''],
    'objectNumber': ['', 'true', '', 'accessionnumber_txt', ''],

    # the rest are mapping the solr field names to django form labels and fields
    'csid': ['id', 'true', '', 'id', ''],
    'accession': ['Accession number', 'true', '', 'accessionnumber_txt', ''],
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
    'blob_ss': ['blob_ss', 'true', '', 'blob_ss', ''],
}


def deURN(urn):
    #find identifier in URN
    m = re.search("\'(.*)\'$", urn)
    if m is not None:
        # strip out single quotes
        return m.group(0)[1:len(m.group(0)) - 1]


def getfields():
    # for solr faceting
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

def doSearch(solr_core, context):
    requestObject = context['searchValues']
    elapsedtime = time.time()
    if 'reset' in requestObject:
        context = {}
    else:
        # create a connection to a solr server
        s = solr.SolrConnection(url='http://localhost:8983/solr/%s' % solr_core)
        queryterms = []
        urlterms = []
        if 'map' in requestObject or 'csv' in requestObject:
            querystring = requestObject['querystring']
        else:
            for p in requestObject:
                if p in ['csrfmiddlewaretoken', 'displayType', 'url', 'querystring', 'facetContext']: continue
                if 'select-' in p: continue # select control for map markers
                if not p in requestObject: continue
                if not requestObject[p]: continue
                if 'item-' in p:
                    continue
                if p == 'keyword':
                    queryterms.append('text:%s' % parseTerm(requestObject[p]))
                    urlterms.append('%s=%s' % (p, cgi.escape(requestObject[p])))
                else:
                    #queryterms.append('(%s LIKE "%s")' % (parms[p][3], requestObject[p]))
                    queryterms.append('%s:"%s"' % (parms[p][3], requestObject[p]))
                    urlterms.append('%s=%s' % (p, cgi.escape(requestObject[p])))
            querystring = ' AND '.join(queryterms)

        if urlterms != []: urlterms.append('displayType=%s' % requestObject['displayType'])
        url = '&'.join(urlterms)
        fqs = {}
        try:
            pixonly = requestObject['pixonly']
        except:
            pixonly = None
        fields = getfields()
        response = s.query(querystring, facet='true',
                           facet_field=fields,
                           fq=fqs,
                           rows=200, facet_limit=40, facet_mincount=1)

        facetflds = getfacets(response)
        print 'num:', response._numFound
        if pixonly:
            results = [r for r in response.results if r.has_key('blobs_ss')]
        else:
            results = response.results

        for i,listItem in enumerate(results):
            item = {}
            item['counter'] = i
            for p in parms:
                try:
                    # make all arrays into strings for display
                    if type(listItem[parms[p][3]]) == type([]):
                        item[p] = ', '.join(listItem[parms[p][3]])
                    else:
                        item[p] = listItem[parms[p][3]]
                except:
                    #raise
                    pass
            # the list of blob csids need to remain an array, so restore it from psql result
            item['blob_ss'] = listItem.get('blob_ss')
            item['marker'] = makeMarker(item)
            context['items'].append(item)

        if requestObject['displayType'] in ['v1','v2', 'grid'] and response._numFound > 30:
            context['recordlimit'] = 'items. (limited to 30 for long display)'
            context['items'] = context['items'][:30]

        context['count'] = response._numFound
        m = {}
        for p in parms: m[parms[p][3].replace('_txt','_s')] = p
        context['fields'] = [m[f] for f in fields]
        context['facetflds'] = [[m[f],facetflds[f]] for f in fields]
        context['range'] = range(len(fields))
        context['fq'] = fqs
        context['url'] = url
        context['pixonly'] = pixonly
        context['querystring'] = querystring
        context['url'] = url
        try:
            context['facetContext'] = requestObject['facetContext']
        except:
            context['facetContext'] = 'none'

    context['core'] = solr_core
    context['time'] = '%8.3f' % (time.time() - elapsedtime)
    return context

#@login_required()
def publicsearch(request):
    solr_core = 'ucjeps-metadata'
    MAXMARKERS = 65

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
            context = doSearch(solr_core, context)
            if 'search' in requestObject:
                pass
            elif 'csv' in requestObject:

                # Create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="ucjeps.csv"'

                #response.write(u'\ufeff'.encode('utf8'))
                writer = csv.writer(response)
                for item in context['items']:
                    #row = [ item[x] if isinstance(x,str) else item[x].encode('utf-8','ignore') for x in item.keys()]
                    #row = [ smart_unicode(item[x].decode('iso-8859-2')) if isinstance(item[x],str) else item[x] for x in item.keys()]
                    #row = [ item[x].decode('utf-8','replace') if isinstance(item[x],unicode) else item[x] for x in item.keys()]
                    row = []
                    for x in item.keys():
                        cell = item[x]
                        if isinstance(item[x],unicode):
                            try:
                                cell = cell.translate({0xd7 : u"x"})
                                cell = cell.decode('utf-8','ignore').encode('utf-8')
                                #cell = cell.decode('utf-8','ignore').encode('utf-8')
                                #cell = cell.decode('utf-8').encode('utf-8')
                            except:
                                print 'unicode problem',cell.encode('utf-8','ignore')
                                cell = u'invalid unicode data'
                        row.append(cell)
                    #print row
                    writer.writerow(row)

                return response

            elif 'map' in requestObject:
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
                context['items'] = mappableitems
                context['mapmsg'] = []
                if len(mappableitems) < context['count'] and context['count'] < MAXMARKERS:
                    context['mapmsg'].append('NB: not all points had latlongs.')
                context['markerlist'] = '&markers='.join(markerlist[:MAXMARKERS])
                if len(markerlist) >= MAXMARKERS:
                    context['mapmsg'].append('%s points is the limit. Only first %s accessions (with latlongs) plotted!' % (MAXMARKERS,len(markerlist)))
            elif 'email' in requestObject:
                pass

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