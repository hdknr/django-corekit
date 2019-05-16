# -*- coding: utf-8 -*-
from django.utils import translation
import djclick as click
from corekit import utils
from corekit.docs.conf import schemaspy_command
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


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


@main.command()
@click.argument('app_label')
@click.option('--subdocs', '-s', is_flag=True)
@click.option('--doctype', '-t', default='rst')
@click.pass_context
def doc_models(self, app_label, subdocs, doctype):
    from django.apps import apps
    from django.db import connections
    con = connections['default']      # TODO
    app = apps.get_app_config(app_label)
    click.echo(utils.render_by(
        f'corekit/db/models.{doctype}',
        app=app, connection=con, subdoc=subdocs))


_format = dict(
    line='{{module}}.{{object_name}} {{db_table}}',
    sphinx='''
.. _{{module}}.{{object_name}}:
{{object_name}}
{{sep}}
.. autoclass:: {{module}}.{{object_name}}
    :members:
''',
)


@main.command()
@click.argument('app_labels', nargs=-1)
@click.option('--format', '-f', default='sphinx', help="format=[line|sphinx]")
@click.pass_context
def list_models(ctx, app_labels, format):
    '''List Models'''
    from django.apps import apps

    for app_label in app_labels:
        conf = apps.get_app_config(app_label)
        for model in conf.get_models():
            data = {
                "app_label": app_label,
                "module": model.__module__,
                "object_name": model._meta.object_name,
                "sep": '-' * len(model._meta.object_name),
                "db_table": model._meta.db_table,
            }
            click.echo(utils.render(_format[format], **data))


@main.command()
@click.option('--database', '-d', default='default')
@click.pass_context
def schemaspy(ctx, database):
    ''' SchemaSpy '''
    click.echo(schemaspy_command(database))
