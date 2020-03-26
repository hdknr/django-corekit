import django

if django.VERSION < (3, 0):
    # https://docs.djangoproject.com/en/3.0/releases/3.0/
    from django.utils.six.moves.urllib.parse import urlparse
else:
    from urllib.parse import urlparse

from django.urls import reverse
from django.template import loader
from django.utils.safestring import mark_safe as _S
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_permission_codename
from mdx_gfm import GithubFlavoredMarkdownExtension
from mimetypes import guess_type
from distutils.util import strtobool
import djclick as click
import markdown
import json
import re
import yaml
import time
import struct
import subprocess


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
    return "admin:{}_{}_change".format(
        instance_or_class._meta.app_label, instance_or_class._meta.model_name)


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
    return re.sub(r'[\s\u3000]', '', src or '')


def render(src, request=None, safe=True, **ctx):
    '''テンプレート文字列でレンダリングする'''

    from django.template import engines
    engine = engines['django']
    request = request or None
    text = engine.from_string(src).render(ctx, request=request)
    return safe and _S(text) or text


def render_by(name, request=None, safe=True, **ctx):
    '''テンプレートファイルでレンダリングする'''
    request = request or None
    text = loader.get_template(name).render(ctx, request=request)
    return safe and _S(text) or text 


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
    if not text:
        return ''
    md = markdown.Markdown(extensions=[GithubFlavoredMarkdownExtension()])
    return _S(md.convert(text)) if safe else md.convert(text)


def is_filetype(path, typename):
    return guess_type (path)[0] == typename


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


def run_at(command, dt):
    '''execute command at specifed datetime'''
    sched_cmd = ['/usr/bin/at', dt.strftime('%H:%M %m/%d/%Y')]
    subprocess.Popen(sched_cmd, stdin=subprocess.PIPE).communicate(command.encode('utf8'))