"""
URL mappings for the Agency application
"""

from django.conf.urls.defaults import patterns, url

from agency import views

agency_url = r'(?P<jurisdiction>[\w\d_-]+)/(?P<slug>[\w\d_-]+)/(?P<idx>\d+)'

urlpatterns = patterns('',
    url(r'^view/%s/$' % agency_url,   views.detail, name='agency-detail'),
    url(r'^update/%s/$' % agency_url, views.update, name='agency-update'),
    url(r'^flag/%s/$' % agency_url,   views.flag, name='agency-flag'),
)