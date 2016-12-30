# -*- coding: utf-8 -*-
from pydoc import locate as load_class
from .methods import CoreModel
import yaml
import json
import os


def load_conf(path):

    def _conf(filepath):
        class_name = os.path.splitext(os.path.basename(filepath))[0]
        for section in yaml.load(open(filepath)):
            load_class(class_name)().load(section)

    if os.path.isfile(path):
        _conf(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                _conf(os.path.join(root, f))


def load_dbtemplates(path):

    def _load(dirname, filename):
        from dbtemplates.models import Template
        name = os.path.join(os.path.basename(dirname), filename)
        content = open(os.path.join(dirname, filename)).read()
        if not Template.objects.filter(name=name).update(content=content):
            Template.objects.create(name=name, content=content)

    if not os.path.isdir(path):
        return
    for root, dirs, files in os.walk(path):
        for f in files:
            _load(root, f)


def load_model_fixtures(model, fixture):

    def _update_or_create(model, fixture, keys, ignores=[]):
        fields = fixture.pop('fields', {})
        qp = dict((k, fields.pop(k, None)) for k in keys)
        map(lambda i: fields.pop(i, None), ignores)
        if not model.objects.filter(**qp).update(**fields):
            fields.update(qp)
            model.objects.create(**fields)

    opt = model._meta
    if opt.app_label == 'dbtemplates' and opt.model_name == 'template':
        _update_or_create(model, fixture, ['name', ], ['sites', ])


def load_fixtures(path):

    data = json.load(open(path))
    for item in data:
        model = CoreModel.contenttype_model(item['model'])
        if hasattr(model.objects, 'load_fixture'):
            model.objects.load_fixture(item)
        else:
            load_model_fixtures(model, item)
