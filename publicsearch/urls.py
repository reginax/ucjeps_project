__author__ = 'amywieliczka'

from django.conf.urls import patterns, url
from publicsearch import views

urlpatterns = patterns('',
                       url(r'^publicsearch/$', views.publicsearch, name='publicSearch'),
                       )