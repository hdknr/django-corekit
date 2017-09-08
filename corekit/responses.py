# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.http import HttpResponse

from .serializers import BaseObjectSerializer as _S
from .files import create_writer, get_mimetype


class CoreFileResponse(HttpResponse):

    def __init__(
        self, content='', filename=None,
        *args, **kwargs
    ):
        content_type = get_mimetype(filename)
        super(CoreFileResponse, self).__init__(
            content, content_type=content_type, *args, **kwargs)

        if filename:
            self.set_filename(filename)

    def set_filename(self, filename):
        self['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            force_text(filename).encode('utf8'))


class ZipballResponse(CoreFileResponse):
    pass


def cors(response, origin='*'):
    response["Access-Control-Allow-Origin"] = origin
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


class JSONResponse(HttpResponse):
    def __init__(self, obj='', json_opts=None, mimetype='application/json',
                 *args, **kwargs):
        json_opts = json_opts if isinstance(json_opts, dict) else {}
        content = _S.to_json(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
        cors(self)


class FileResponse(HttpResponse):
    def __init__(
        self, content='', filename=None,
        content_type='application/octet-stream',
        *args, **kwargs
    ):
        if filename:
            content_type = get_mimetype(filename)

        super(FileResponse, self).__init__(
            content, content_type=content_type, *args, **kwargs)

        # Writer
        self.writer = create_writer(content_type, self, **kwargs)

        if filename:
            self.set_filename(filename)

    def set_filename(self, filename):
        self['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            force_text(filename).encode('utf8'))

    def serialize(self, serializer, *args, **kwargs):
        items = iter(serializer.data)
        data = items.next()
        self.writer.writerow(data.keys())
        self.writer.writerow(data.values())

        for data in items:
            self.writer.writerow(data.values())
        self.writer.close()
        return self
