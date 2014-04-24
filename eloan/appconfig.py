# global variables

from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'eloan')

MAXMARKERS = int(config.get('eloan', 'MAXMARKERS'))
MAXRESULTS = int(config.get('eloan', 'MAXRESULTS'))
MAXLONGRESULTS = int(config.get('eloan', 'MAXLONGRESULTS'))
MAXFACETS = int(config.get('eloan', 'MAXFACETS'))
IMAGESERVER = config.get('eloan', 'IMAGESERVER')
BMAPPERSERVER = config.get('eloan', 'BMAPPERSERVER')
BMAPPERDIR = config.get('eloan', 'BMAPPERDIR')
BMAPPERCONFIGFILE = config.get('eloan', 'BMAPPERCONFIGFILE')
SOLRSERVER = config.get('eloan', 'SOLRSERVER')
SOLRCORE = config.get('eloan', 'SOLRCORE')
SOLRQUERYPARAM = config.get('eloan', 'SOLRQUERYPARAM')
LOCALDIR = config.get('eloan', 'LOCALDIR')
DROPDOWNS = config.get('eloan', 'DROPDOWNS').split(',')
SEARCH_QUALIFIERS = config.get('eloan', 'SEARCH_QUALIFIERS').split(',')