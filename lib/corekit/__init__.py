# coding: utf-8
#
VERSION = (0, 1, 1, 'beta', 0)
default_app_config = 'corekit.apps.CorekitConfig'


def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version
