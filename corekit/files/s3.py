# coding: utf-8
from django.conf import settings
from django.core.urlresolvers import reverse

from storages.backends.s3boto import S3BotoStorage


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION

    def url(self, name, headers=None, response_headers=None, expire=None):
        if name and name.startswith('protected'):
            return reverse('corekit_download_stub', kwargs={'name': name})

        res = super(MediaStorage, self).url(
            name, headers=headers, response_headers=response_headers,
            expire=expire)
        return res
