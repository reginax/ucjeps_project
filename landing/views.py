__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings


TITLE = 'Applications Available'

hiddenApps = 'hello service suggest suggestsolr suggestpostgres solarapi imageserver landing'.split(' ')

#@login_required()
def index(request):
    appList = []
    for app in settings.INSTALLED_APPS:
        if not "django" in app and not app in hiddenApps:
            if app == 'eloan' or app == 'publicsearch':
                app = 'public/' + app
            appList.append(app)
    appList.sort()
    return render(request, 'listApps.html', {'appList': appList, 'labels': 'name file'.split(' '), 'title': TITLE})
