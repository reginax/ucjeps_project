__author__ = 'jblowe'

from django.conf.urls import patterns, url
from taxoneditor import views

urlpatterns = patterns('',
                       url(r'^$', views.taxoneditor, name='index'),
                       )
