# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Context, Template, loader
from django.utils.safestring import mark_safe as _S
from django.utils.six.moves.urllib.parse import urlparse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_permission_codename
from django.utils import six
from django import VERSION

if six.PY3:
    import io
    contents = io.BytesIO
else:
    import StringIO
    contents = StringIO.StringIO

import markdown
import json
from mdx_gfm import GithubFlavoredMarkdownExtension
from mimetypes import guess_type
from distutils.util import strtobool
import djclick as click
import re
import yaml
import time
import struct


def get_absolute_url(instance, name='detail'):
    return reverse(
        '{0}_{1}_{2}'.format(
            instance._meta.app_label, instance._meta.model_name, name),
        kwargs={'id': instance.id})


def get_contenttype(instance_or_class):
    if isinstance(instance_or_class, ContentType):
        return instance_or_class
    return ContentType.objects.get_for_model(instance_or_class)


def to_natural_key(instance_or_class):
    return get_contenttype(instance_or_class).natural_key()


def to_natural_key_string(instance_or_class):
    return ".".join(to_natural_key(instance_or_class))


def from_natual_key(app_lable, model_name, **queries):
    ct = ContentType.objects.get_by_natural_key(app_lable, model_name)
    if queries:
        return ct.get_object_for_this_type(**queries)
    return ct.model_class()


def from_natual_key_string(natural_key_string, **queries):
    return from_natual_key(*natural_key_string.split('.'), **queries)


def get_permission(ct_or_model, codename):
    ct = get_contenttype(ct_or_model)
    return ct.permission_set.filter(codename=codename).first()


def get_perm_name(model, action):
    '''指定されたアクションに対するパーミッション名'''
    return "{}.{}".format(
        model._meta.app_label, get_permission_codename(action, model._meta))


def to_admin_change_url_name(instance_or_class):
    return "admin:{}_{}_change".format(instance_or_class._meta.app_label)


def to_admin_change_url(instance_or_class, id=None):
    id = id or instance_or_class.id
    return reverse(
        to_admin_change_url_name(instance_or_class), args=[id])


def to_admin_changelist_url_name(instance_or_class):
    return 'admin:{0}_changelist'.format(instance_or_class._meta.db_table)


def to_admin_changelist_url(instance_or_class):
    return reverse(to_admin_changelist_url_name(instance_or_class))


def spaceless(src):
    '''空白を取り除く'''
    return re.sub(ur'[\s\u3000]', '', src or '')


def render(src, ctxobj=None, request=None, **ctx):
    '''テンプレート文字列でレンダリングする'''

    ctxobj = ctxobj or Context(ctx)
    return _S(Template(src).render(ctxobj, request=request))


def render_by(name, ctxobj=None, request=None, **ctx):
    '''テンプレートファイルでレンダリングする'''
    if VERSION > (1, 10):
        ctxobj = ctx
    else:
        ctxobj = ctxobj or Context(ctx)
    return _S(loader.get_template(name).render(ctxobj, request=request))


def echo(teml, fg="green", **kwargs):
    '''テンプレートでコンソールに書き出す '''
    click.secho(render(teml, **kwargs), fg=fg)


def echo_by(name, fg="green", **kwargs):
    '''テンプレートでコンソールに書き出す '''
    click.secho(render_by(name, **kwargs), fg=fg)


def force_bool(value):
    '''強制的に論理値に変換'''
    try:
        return strtobool(u"{}".format(value)) == 1
    except:
        pass
    return False


def get_mimetype(file_name):
    '''ファイルのmimetypeを返す'''
    if not file_name or file_name.startswith('__MACOSX/'):
        return [None, None]
    name, _x = guess_type(file_name)
    return name and name.split('/') or [None, None]


def list_to_choices(choices):
    return tuple((choices.index(i), i) for i in choices)


def to_gfm(text, safe=True):
    '''Github Favored Markdown'''
    md = markdown.Markdown(extensions=[GithubFlavoredMarkdownExtension()])
    return _S(md.convert(text)) if safe else md.convert(text)


def convert(source, format='yaml'):
    if format in ['yaml', 'yml']:
        return yaml.load(source)
    if format == 'json':
        return json.loads(source)


def load_template(name):
    '''名前で指定されたテンプレートのソース'''
    return loader.get_template(name).template.source


def time_serial():
    '''時間のシリアル値を16進数で返す'''
    return struct.pack('d', time.time()).encode('hex')


def url(url_string):
    '''urlparse'''
    return urlparse(url_string)


def permcode_items(perm_code):
    p = re.split(r"[._]", perm_code) + [None, None, None]
    return dict(zip(['app_label', 'action', 'model'], p[:3]))
