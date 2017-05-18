# -*- coding: utf-8 -*-
from django.utils import translation
from django.core.cache import cache

from corekit.conf import load_conf, load_fixtures
from corekit import methods, querysets, utils
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
@click.option('--database', '-d', default='default')
@click.pass_context
def createdb_sql(ctx, database):
    '''create database'''
    from django.conf import settings
    conf = settings.DATABASES.get(database)
    click.echo(utils.render_by(
        'corekit/db/createdb.sql', conf=conf))
