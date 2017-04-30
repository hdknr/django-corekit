# -*- coding: utf-8 -*-
from django.utils import translation
from django.core.cache import cache

from corekit.conf import load_conf, load_fixtures
from corekit import methods, querysets
import djclick as click
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


@main.command()
@click.argument('path')
@click.pass_context
def config(ctx, path):
    '''Load YAML'''
    load_conf(path)


@main.command()
@click.argument('path')
@click.pass_context
def fixtures(ctx, path):
    '''load fixture'''
    load_fixtures(path)


@main.command()
@click.pass_context
def cache_clear(ctx):
    cache.clear()


@main.command()
@click.argument('model')
@click.pass_context
def zipball(ctx, model):
    model_class = methods.CoreModel.contenttype_model(model)
    with open('/tmp/{}.zip'.format(model), 'w') as zipfile:
        querysets.CoreQuerySet(model_class).zipball(zipfile)


@main.command()
@click.pass_context
def ipafont(ctx):
    '''IPA Font'''
    from io import BytesIO
    import requests
    import zipfile
    url = 'http://dl.ipafont.ipa.go.jp/IPAexfont/IPAexfont00301.zip'
    zf = zipfile.ZipFile(BytesIO(requests.get(url).content))
    zf.extractall()
