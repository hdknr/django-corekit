# -*- coding: utf-8 -*-
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pydoc import locate as load_class
from .methods import CoreModel
import yaml
import json
import os
import traceback
from logging import getLogger
logger = getLogger()


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


class ConfLoader(object):
    def load(self, conf):
        raise NotImplemented


class GroupPermissionLoader(ConfLoader):

    def permit_action(self, group, content_type, action):
        try:
            codename = get_permission_codename(
                action, content_type.model_class()._meta)

            perms = Permission.objects.filter(
                content_type=content_type, codename=codename)
            name = "Can {} {}".format(
                action, content_type.model_class()._meta.verbose_name_raw)
            if perms.exists():
                perms.update(name=name)
                pobj = perms.first()
            else:
                pobj = Permission.objects.create(
                    content_type=content_type, codename=codename, name=name)

            group.permissions.add(pobj)
        except:
            logger.error(u"Permission failure:{} {}.{}".format(
                action, content_type.app_label, content_type.model))
            logger.error(traceback.format_exc())

    def load(self, conf):
        for item in conf['groups']:
            group, _x = Group.objects.get_or_create(name=item['group'])
            for perm in item['permissions']:
                content_type = ContentType.objects.get_by_natural_key(
                    *perm['model'].split('.'))
                for action in perm['actions']:
                    self.permit_action(group, content_type, action)
