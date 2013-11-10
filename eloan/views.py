__author__ = 'jblowe, rjaffe'

import re
import time

from django.shortcuts import render
import urllib
from cspace_django_site.main import cspace_django_site
from authenticatedReqUtil import get_entity
from publicsearch.utils import writeCsv, doSearch, setupGoogleMap, setupBMapper, getfromXML

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

# global variables (at least to this module...)
config = cspace_django_site.getConfig()

# Static string parts for publicsearch (Solr) query
SOLRSERVER = 'http://localhost:8983/solr'
SOLRQUERYPARAMCSID = 'csid'
SOLRQUERYPARAMACCESSION = 'accession'
SOLRCORE = 'ucjeps-metadata'

# CONSTANTS
TIMESTAMP = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

SEARCHRESULTS = {}

TITLE = 'eLoan'

#@login_required()
def eloan(request):
    if 'kw' in request.GET and request.GET['kw']:
        eloanNum = urllib.quote_plus(request.GET['kw'])
        eloanNum = str(eloanNum)

        if 'recType' in request.GET and request.GET['recType']:
           recType = urllib.quote_plus(request.GET['recType'])
           recType = str(recType)
        #TODO Make this else clause error message work so value can be entered by user and form can be generalizable.
        #else send error message: "Please enter the type of record in which the keyword can be found"
        # Do this as Javascript validation?
        # TEMP FIX
        else:
            recType = 'loansout'

        #################################################################
        #  GET ELOAN INFORMATION AND RELATED OBJECTS FROM CSPACE-SERVICES
        #################################################################

        #  get eloan list-item
        asquery = '%s?as=%s_common%%3AloanOutNumber%%3D%%27%s%%27&wf_deleted=false'  % (recType, recType, eloanNum,)

        expectedmimetype = 'application/xml'

        # Make authenticated connection to ucjeps.cspace...
        lolistdata = get_entity(request, asquery, expectedmimetype).content
        loanoutlistXML = fromstring(lolistdata)

        # To grab everything: loinfo = loanoutlistXML.find('.//list-item')
        # To grab just the Loanout CSID:
        try:
            locsid = loanoutlistXML.find('.//list-item/csid')
            locsid = locsid.text
        except:
            errMsg = "Could not find the loan %s. Please try another." % eloanNum
            print(errMsg)
            # TODO: FIX THIS - Should write simple message on screen: "Could not find that loan. Please try another" and ...
            # TODO (cont.) return browser to http://localhost:8000/public/eloan/ or include a link back.
            raise Exception(errMsg)

        # get eloan record
        loquery = '%s/%s' % (recType, locsid)

        # Make authenticated connection to ucjeps.cspace...
        lodata = get_entity(request, loquery, expectedmimetype).content
        loanoutXML = fromstring(lodata)

        # Start gathering loan out info into results: eloan number (already have), borrower's contact and eloan date.
        loaninfo = []
        loaninfo.append(eloanNum)

        borcontact = getfromXML(loanoutXML,'.//borrowersContact')
        loaninfo.append(borcontact)

        lodate = getfromXML(loanoutXML,'.//loanOutDate')
        loaninfo.append(lodate)

        # Get related collection objects; some pertinent info can be gleaned from list results
        # Record type hard-coded for now. Generalize this?
        roquery = '%s?sbj=%s&objType%%3D%%27%s' %  ('relations', locsid, 'collectionobject')

        # Make authenticated connection to ucjeps.cspace...
        rolistdata = get_entity(request, roquery,  expectedmimetype).content
        relatedObjListXML = fromstring(rolistdata)
        relatedObjXML = relatedObjListXML.findall('./relation-list-item')

        # loanItemInfo = []
        objectCsids = []
        objectNumbers = []
        for i in relatedObjXML:

            objCsid = getfromXML(i,'./object/csid')
            objectCsids.append(objCsid)

            # Other options ...
            # if we ever need objectNumber and objectName

            # Note: ObjectNumber not a required field in UCJEPS instance, so using it for search is problematic
            objNum = getfromXML(i,'./object/number')
            # objNum = '' if objNum is None else objNum
            objectNumbers.append(objNum)

            # Note: ObjectName not necessarily unique, so using it for search is problematic
            # objName = getfromXML(i,'./object/name')
            # objName = '' if objectName is None else objectName.text
            # objectNames.append(objName)


        ##################
        # AT THIS POINT, SWITCH TO SOLR SEARCH
        # Use objCsid values to search publicsearch webapp via doSearch method of publicsearch.utils
        # Write search results to a div below the loan out info.
        # TODO: Need to incorporate typeSpecimenBasionym field into solr data source and template.
        ##################

        # Build args to pass to solr
        # Static string parts of the URL
        solr_server = SOLRSERVER
        solr_queryparamcsid = SOLRQUERYPARAMCSID
        solr_queryparamacc = SOLRQUERYPARAMACCESSION
        solr_core = SOLRCORE

        # Pull individual CSIDs from list of objectCsids (i.e., CSIDs of objects related to the loan)
        # Insert ' OR ' between each CSID
        csidsToSearch = " OR ".join(objectCsids)
        objectNumbersToSearch = " OR ".join(objectNumbers)
        query_dictionary = {solr_queryparamcsid:csidsToSearch, solr_queryparamacc:objectNumbersToSearch, 'displayType':'full', 'maxresults':'2000'}
        solr_context = {'searchValues':query_dictionary}
        # solr_context['resultsOnly'] = 'true'

        results = doSearch(solr_server, solr_core, solr_context)

        # Either break values out of results array as we do here, or use results[value] notation in HTML templates
        return render(request, 'eloan.html',
            {'loaninfo': loaninfo, 'results': results, 'items': results['items'], 'displayType': results['displayType'], 'count': results['count'], 'imageserver': results['imageserver'], 'url': results['url'], 'querystring': results['querystring'], 'timestamp': results['timestamp'], 'time': results['time'], 'kw': eloanNum})

    else:
        return render(request, 'eloan.html', {'title': TITLE, 'timestamp': TIMESTAMP })
