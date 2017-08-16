# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.core.files.storage import FileSystemStorage
from django.utils import encoding
from django.urls import reverse
from django import VERSION

from .csvutils import CsvReader, CsvWriter
from .xlsxutils import XlsxReader, XlsxWriter, XlsxBaseReader

import mimetypes

import traceback
from urllib import unquote as UQ
import os

from logging import getLogger
logger = getLogger()


@deconstructible
class UploadPath(object):
    def __init__(self, access='protected', fieldname=None):
        self.fieldname = fieldname or 'file'
        self.access = access

    def __call__(self, instance, filename):
        try:
            name = self.create_name(instance, filename)
            res = self.get_filepath(
                self.access, instance._meta.app_label,
                instance._meta.model_name, self.fieldname, name)
            return res
        except:
            logger.error(traceback.format_exc())

    def create_name(self, instance, filename):
        return filename and u"{}{}".format(
            instance.id, os.path.splitext(filename)[1])

    @classmethod
    def get_base_url(cls, access, app_label, model_name, field_name):
        return u'{}/{}/{}/{}'.format(
            access, app_label, model_name, field_name)

    @classmethod
    def get_filepath(cls, access, app_label, model_name, field_name, name):
        name = encoding.force_text(name)
        ret = u'{}/{}'.format(
            cls.get_base_url(access, app_label, model_name, field_name), name)

        return UQ(ret) if VERSION > (1, 10) else UQ(ret).decode('utf8')


def get_local_storage(base_dir, access, app_label, model_name, field_name):
    base_url = '/' + UploadPath.get_base_url(
        access, app_label, model_name, field_name)
    storage = FileSystemStorage(
        location=os.path.join(settings.BASE_DIR, base_dir), base_url=base_url)
    return storage


DEFAULT_MIMETYPE = 'text/csv'


def get_mimetype(path):
    return mimetypes.guess_type(path)[0] or DEFAULT_MIMETYPE


def create_reader(mimetype, path, headless=False, *args, **kwargs):
    if mimetype == CsvReader.MIMETYPE:
        return CsvReader(open(path, 'rU'), *args, **kwargs)

    if 'encoding' in kwargs:
        kwargs.pop('encoding')
    if headless:
        return XlsxBaseReader(open(path), *args, **kwargs)
    return XlsxReader(open(path), *args, **kwargs)


def create_writer(mimetype, *args, **kwargs):
    return {
        CsvWriter.MIMETYPE: CsvWriter,
        XlsxWriter.MIMETYPE: XlsxWriter,
    }[mimetype](*args, **kwargs)


class FileStorage(FileSystemStorage):

    def url(self, name, headers=None, response_headers=None, expire=None):
        if name and name.startswith('protected'):
            return reverse('corekit_download_stub', kwargs={'name': name})
        res = super(FileStorage, self).url(
            name, headers=headers, response_headers=response_headers,
            expire=expire)
        return res
