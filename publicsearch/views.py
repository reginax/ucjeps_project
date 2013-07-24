__author__ = 'amywieliczka'

import os
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django import forms

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

from common import cspace
from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()

def deURN(urn):
    #find identifier in URN
    m = re.search("\'(.*)\'$", urn)
    if m is not None:
        # strip out single quotes
        return m.group(0)[1:len(m.group(0))-1]

@login_required()
def publicsearch(request):
    context = {'items': [], 'searchValues': request.POST}
    
    if request.method == 'POST':
        form = forms.Form(request.POST)
        
        if form.is_valid():
            # create keyword search query
            if len(request.POST['keyword']) is not 0:
                query = 'kw=' + quote(request.POST['keyword'])
            
            # otherwise, create advanced search query
            else:
                string=''
                for p in request.POST:
                    if p != 'csrfmiddlewaretoken' and len(request.POST[p]) is not 0:
                        # for query term concatentation
                        if (len(string) > 0): string = string + ' AND '
                        string = string + p + '="' + request.POST[p] + '"'
                query = 'as=' + quote(string)
            
            connection = cspace.connection.create_connection(config, request.user)
            (url, data, statusCode) = connection.make_get_request('cspace-services/collectionobjects?%s' % query)
            
            if (statusCode == 200):
                for listItem in fromstring(data).findall('list-item'):
                    item = {
                        'uri': listItem.find('uri').text,
                        'csid': listItem.find('csid').text,
                        'objectNumber': '',
                        'taxon': ''
                    }
                    
                    if listItem.find('objectNumber') is not None:
                        item['objectNumber'] = listItem.find('objectNumber').text
                    if listItem.find('taxon') is not None:
                        item['taxon'] = deURN(listItem.find('taxon').text)
                    
                    context['items'].append(item)
                    
                
            
        
    return render(request, 'publicsearch.html', context)