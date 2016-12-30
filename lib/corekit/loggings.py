# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.debug import ExceptionReporter
from django.conf import settings
from logging import Handler
from copy import copy
import requests
import json


class LogHandler(Handler, object):

    def __init__(self, slack_webhook=None):
        Handler.__init__(self)
        self.slack_webhook = slack_webhook

    def emit(self, record):
        from core import utils
        try:
            request = record.request
        except Exception:
            request = None

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = ExceptionReporter(request, is_email=False, *exc_info)

        day = timezone.now().strftime('%Y-%m-%d')
        storage = FileSystemStorage()
        name = storage.save(
            'exception/{}/error.html'.format(day),
            ContentFile(reporter.get_traceback_html()))

        try:
            path = reverse('core_exception', kwargs={'path': name})

            if request:
                url = request.build_absolute_uri(path)
            else:
                url = path

            text = utils.render(
                '{{ exception_type }}:'
                '{% if request %} {{ request.path_info|escape }}\n{% endif %}'
                '{% if exception_value %}{{ exception_value|force_escape }}'
                '{% endif %} <{{ url }}>',
                url=url, **reporter.get_traceback_data())

            self.slack({"text": text})
        except:
            pass

    def slack(self, payload):
        if not self.slack_webhook or not getattr(settings, 'USE_SLACK', False):
            return
        try:
            requests.post(
                self.slack_webhook,
                data=json.dumps(payload), timeout=3, allow_redirects=False)
        except:
            pass
