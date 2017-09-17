#!/usr/bin/python
# coding: utf-8

# maposmatic, the web front-end of the MapOSMatic city map generation system
# Copyright (C) 2009  David Decotigny
# Copyright (C) 2009  Frédéric Lehobey
# Copyright (C) 2009  David Mentré
# Copyright (C) 2009  Maxime Petazzoni
# Copyright (C) 2009  Thomas Petazzoni
# Copyright (C) 2009  Gaël Utard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import django
from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from .maposmatic import feeds
from .maposmatic import views
from . import settings

urlpatterns = patterns('',
    url(r'^$',
        views.index,
        name='main'),

    url(r'^new/$',
        views.new,
        name='new'),
    url(r'^recreate/$',
        views.recreate,
        name='recreate'),
    url(r'^cancel/$',
        views.cancel,
        name='cancel'),

    url(r'^maps/(?P<id>\d+)/(?P<nonce>[A-Za-z]{16})$',
        views.map_full,
        name='map-by-id-and-nonce'),
    url(r'^maps/(?P<id>\d+)$',
        views.map_full,
        name='map-by-id'),
    url(r'^maps/$',
        views.maps,
        name='maps'),

    url(r'^about/$',
        views.about,
        name='about'),
    url(r'^donate/$',
        views.donate,
        name='donate'),
    url(r'^donate-thanks/$',
        views.donate_thanks,
        name='donate-thanks'),

    (r'^apis/nominatim/$', views.api_nominatim),
    (r'^apis/reversegeo/([^/]*)/([^/]*)/$', views.api_nominatim_reverse),
    (r'^apis/papersize', views.api_papersize),
    (r'^apis/boundingbox/([^/]*)/$', views.api_bbox),
    (r'^apis/polygon/([^/]*)/$', views.api_polygon),

    # Feeds
    django.VERSION[1] >= 4 and \
        url(r'^feeds/maps/', feeds.MapsFeed(),
            name='rss-feed') or \
        url(r'^feeds/(?P<url>.*)/$',
            'django.contrib.syndication.views.feed',
            {'feed_dict': {'maps': feeds.MapsFeed}},
            name='rss-feed'),

    # Internationalization
    (r'^i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    urlpatterns.extend(patterns('',
        (r'^results/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.RENDERING_RESULT_PATH}),

        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.LOCAL_MEDIA_PATH}),
    ))
