# -*- coding: utf-8 -*-
from django import shortcuts
from django.conf import urls, settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import (
    decorators as auth_decos, models as auth_models,
    logout as auth_logout)
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.query import Prefetch
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator as _M
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
import os
import mimetypes

from mimetypes import guess_type
from functools import wraps, partial
from . import methods, querysets, responses, utils
from operator import itemgetter


never_cache = never_cache


class View(object):
    def __init__(self, request, *args):
        self.request = request

    @classmethod
    def handler(cls, url='', name='', order=0, decorators=None, perms=[]):
        decorators = decorators or [lambda x: x]
        if perms:
            decorators += [auth_decos.permission_required(p) for p in perms]

        def _handler(func):

            @wraps(func)
            def wrapper(cls, *args, **kwargs):
                # first argument is `cls`
                response = func(cls(*args), *args, **kwargs)
                return response

            wrapper.url = url
            wrapper.name = name
            wrapper.reverse = partial(reverse, name)
            wrapper.order = order
            return classmethod(
                reduce(lambda x, y: _M(y)(x), [wrapper] + decorators))

        return _handler

    @classmethod
    def urls(cls):
        ''' list of urlpattern'''
        def _cache():
            funcs = []
            for name in cls.__dict__:
                obj = getattr(cls, name)
                if hasattr(obj, 'url'):
                    viewname = obj.name
                    funcs.append((viewname, obj.order, obj))

            # sort by `obj.order`
            cls._urls = [
                urls.url(func.url, func, name=name)
                for name, _, func in sorted(funcs, key=itemgetter(1))
            ]
            cls._handlers = dict(
                (u.callback.im_func.func_name, u.name) for u in cls._urls)
            return cls._urls
        return hasattr(cls, '_urls') and cls._urls or _cache()

    @property
    def handlers(self):
        return self._handlers

    @classmethod
    def requires(self, perm_code):
        ''' perm_code permission is REQUIRED '''
        if perm_code == 'login':
            return auth_decos.login_required
        return auth_decos.permission_required(perm_code)

    @classmethod
    def recent(self, hours=1, **kwargs):
        '''authentication action is REQUIED in last `hours` '''
        def _test(user):
            now = timezone.now()
            span = now - user.last_login
            return (span.seconds < hours * 3600)
        return auth_decos.user_passes_test(_test, **kwargs)

    def render(self, template_name, with_cors=False, **kwargs):
        res = TemplateResponse(
            self.request, template_name,
            dict(view=self, request=self.request, **kwargs))
        return with_cors and responses.cors(res) or res

    def render_source(self, source, with_cors=False, **kwargs):
        res = HttpResponse(
            utils.render(
                source, RequestContext(self.request, kwargs)))
        return with_cors and responses.cors(res) or res

    @classmethod
    def redirect(cls, *args, **kwargs):
        return shortcuts.redirect(*args, **kwargs)

    def logout_to(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth_logout(self.request)
        return shortcuts.redirect(*args, **kwargs)

    def json(self, data, *args, **kwargs):
        return responses.JSONResponse(data)

    def permission_error(self):
        raise PermissionDenied

    def clear_cache(self):
        cache.clear()

    def page_not_found(self):
        raise Http404

    def not_authorized(self, msg='Unauthorized'):
        return HttpResponse(msg, status=401)

    def serialize(self, serializer, filename, res=responses.FileResponse):
        return res(filename=filename).serialize(serializer)


handler = View.handler


@staff_member_required
def exception(request, path):
    ''' publish exception exception'''
    try:
        ct, _ = guess_type(path)
        res = HttpResponse(
            FileSystemStorage().open(path), content_type=ct)
        return res
    except:
        return responses.JSONResponse(['Error'])


@staff_member_required
def groups(request):
    ''' Group'''
    app_label = request.GET.get('app_label', None)
    if app_label:
        prefetch = Prefetch(
            'permissions',
            queryset=auth_models.Permission.objects.filter(
                content_type__app_label=app_label))

        groups = auth_models.Group.objects.filter(
            permissions__content_type__app_label=app_label
        ).prefetch_related(prefetch).distinct()

    else:
        groups = auth_models.Group.objects.exclude(
            permissions__isnull=True)

    app_labels = ContentType.objects.filter(
        permission__group__isnull=False).values_list(
            'app_label', flat=True).distinct()

    return TemplateResponse(
        request,
        'core/groups.html',
        dict(request=request, groups=groups, app_labels=app_labels,
             title=_(u'Groups and Premission')))


def download(request, access, app_label, model_name, field_name, path):
    '''download file'''
    ct = ContentType.objects.get(app_label=app_label, model=model_name)
    model_class = ct.model_class()
    action = 'download_{}'.format(field_name)
    perm = methods.CoreModel.perm_name(action, model=model_class)
    full = "{}/{}/{}/{}/{}".format(
        access, app_label, model_name, field_name, path)
    query = Q(**{field_name: path}) | Q(**{field_name: full})
    instance = model_class.objects.filter(query).first()
    if access == 'protected' and not request.user.has_perm(perm, instance):
        return HttpResponseForbidden()

    value = getattr(instance, field_name)
    ct, _x = guess_type(path)
    res = HttpResponse(value, content_type=ct)
    return res


def download_stub(request, name):
    '''Fake view'''
    pass


@staff_member_required
def zipball(request, model):
    '''return Zipped model fixtures'''
    res = responses.ZipballResponse(filename="{}.zip".format(model))
    model_class = methods.CoreModel.contenttype_model(model)
    querysets.CoreQuerySet(model_class).zipball(res)
    return res


def static(request, path, dir_name='', base_dir=None):
    if path == '' or path.endswith('/'):
        path = path + "index.html"
    base_dir = base_dir or settings.BASE_DIR
    abspath = os.path.join(os.path.join(base_dir, dir_name), path)
    mt, dmy = mimetypes.guess_type(abspath)
    return HttpResponse(
        File(open(abspath)), content_type=mt)
