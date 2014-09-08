# global variables

from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'search')

MAXMARKERS = int(config.get('search', 'MAXMARKERS'))
MAXRESULTS = int(config.get('search', 'MAXRESULTS'))
MAXLONGRESULTS = int(config.get('search', 'MAXLONGRESULTS'))
MAXFACETS = int(config.get('search', 'MAXFACETS'))
IMAGESERVER = config.get('search', 'IMAGESERVER')
BMAPPERSERVER = config.get('search', 'BMAPPERSERVER')
BMAPPERDIR = config.get('search', 'BMAPPERDIR')
BMAPPERCONFIGFILE = config.get('search', 'BMAPPERCONFIGFILE')
SOLRSERVER = config.get('search', 'SOLRSERVER')
SOLRCORE = config.get('search', 'SOLRCORE')
LOCALDIR = config.get('search', 'LOCALDIR')
DROPDOWNS = config.get('search', 'DROPDOWNS').split(',')
SEARCH_QUALIFIERS = config.get('search', 'SEARCH_QUALIFIERS').split(',')
TITLE = config.get('search', 'TITLE')

# still need to move this into a config file.
# could be the same one as above, or a different one.
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
    'updatedat': ['Last updated at', 'true', '', 'updatedat_dt', ''],
    'previousdeterminations': ['Previous Determinations', 'true', '', 'previousdeterminations_ss', ''],
    'localname': ['Local Name', 'true', '', 'localname_txt', ''],
    'briefdescription': ['Description', 'true', '', 'briefdescription_txt', ''],
    'associatedtaxa': ['Associated Taxa', 'true', '', 'associatedtaxa_ss', ''],
    'typeassertions': ['Type Assertions', 'true', '', 'typeassertions_ss', ''],
    'othernumbers': ['Other Numbers', 'true', '', 'othernumbers_ss', ''],
    'labelheader': ['Label Header', 'true', '', 'labelheader_txt', ''],
    'labelfooter': ['Label Footer', 'true', '', 'labelfooter_txt', ''],
    'depth': ['Depth', 'true', '', 'depth_txt', ''],
    'mindepth': ['Min. Depth', 'true', '', 'mindepth_txt', ''],
    'maxdepth': ['Max. Depth', 'true', '', 'maxdepth_txt', ''],
    'depthunit': ['Depth Unit', 'true', '', 'depthunit_txt', ''],
    'sex': ['Sex', 'true', '', 'sex_s', ''],
    'phase': ['Phase', 'true', '', 'phase_s', ''],
    'determinationdetails': ['Determination Details', 'true', '', 'determinationdetails_txt', ''],
    'blobs': ['blob_ss', 'true', '', 'blob_ss', ''],
}
