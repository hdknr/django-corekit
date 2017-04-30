# -*- coding: utf-8 -*-
from django.utils import translation
import djclick as click
from corekit import utils
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
@click.option('--subdocs', is_flag=True)
@click.pass_context
def generate_doc(self, app_label, subdocs):
    from django.apps import apps
    from django.db import connections
    con = connections['default']      # TODO
    app = apps.get_app_config(app_label)
    click.echo(utils.render_by(
        'corekit/db/models.rst',
        app=app, connection=con, subdoc=subdocs))
