# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^zipball/(?P<model>.+)', views.zipball, name="corekit_zipball",),
    url(r'^download/(?P<access>[^/]+)/(?P<app_label>[^/]+)/(?P<model_name>[^/]+)/(?P<field_name>[^/]+)/(?P<path>.+)',       # NOQA
        views.download, name="corekit_download",),
    url(r'^download/(?P<name>.+)',
        views.download_stub, name="corekit_download_stub",),
    url(r'^groups', views.groups, name="corekit_groups",),
    url(r'^(?P<path>exception/.+)', views.exception, name="corekit_exception",),
]
