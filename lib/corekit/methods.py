# coding: utf-8
from __future__ import unicode_literals
from django.db.models import BooleanField
from django.db.models.fields.related import OneToOneRel, RelatedField
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_permission_codename
from django.utils.safestring import mark_safe as _S
from django.forms.models import model_to_dict


from itertools import chain
from utils import force_bool
import re
from .serializers import BaseObjectSerializer as Sz


class CoreModel(object):
    def get_absolute_url(self):
        return reverse(
            '{0}_{1}_detail'.format(
                self._meta.app_label, self._meta.model_name),
            kwargs={'id': self.id})

    def get_edit_url(self):
        return reverse(
            '{0}_{1}_edit'.format(
                self._meta.app_label, self._meta.model_name),
            kwargs={'id': self.id})

    @classmethod
    def admin_change_url_name(cls, model=None):
        model = model or cls
        return 'admin:{0}_{1}_change'.format(
            model._meta.app_label, model._meta.model_name, )

    def admin_change_url(self, instance=None):
        instance = instance or self
        return reverse(
            self.admin_change_url_name(instance), args=(instance.id, ))

    @classmethod
    def admin_changelist_url_name(cls, model=None):
        model = model or cls
        return 'admin:{0}_{1}_changelist'.format(
            model._meta.app_label, model._meta.model_name)

    @classmethod
    def admin_changelist_url(cls, model=None):
        model = model or cls
        return reverse(cls.admin_changelist_url_name(model))

    @classmethod
    def contenttype(cls, model=None):
        model = model or cls
        for_concrete_model = not model._meta.proxy
        return ContentType.objects.get_for_model(
            model, for_concrete_model=for_concrete_model)

    @classmethod
    def contenttype_model(cls, content_type_key):
        app_label, model = content_type_key.split('.')
        ct = ContentType.objects.get_by_natural_key(app_label, model)
        return ct and ct.model_class()

    @classmethod
    def contenttype_instance(cls, content_type_key, id):
        app_label, model = content_type_key.split('.')
        ct = ContentType.objects.get_by_natural_key(app_label, model)
        return ct and ct.get_object_for_this_type(id=id)

    @classmethod
    def permission(cls, codename, model=None):
        model = model or cls
        return cls.contenttype(model).permission_set.filter(
            codename=codename).first()

    @classmethod
    def perm_name(cls, action, model=None):
        '''指定されたアクションに対するパーミッション名'''
        model = model or cls
        return "{}.{}".format(
            model._meta.app_label,
            get_permission_codename(action, model._meta))

    @classmethod
    def perm_code(cls, action, model=None):
        '''perm_code for given action'''
        model = model or cls
        return get_permission_codename(action, model._meta)

    @classmethod
    def can(cls, user, action, model):
        perm = cls.perm_name(action, model)
        return user.has_perm(perm, model)

    @classmethod
    def sql_select_fields(cls, prefix=None, starts=0, model=None):
        model = model or cls
        prefix = prefix and prefix + "." or ""
        return [_S(u"{}{}".format(prefix, f.name))
                for f in model._meta.fields[starts:]]

    @classmethod
    def get_all_related_objects(cls, model=None):
        '''http://bit.ly/2aJ4Z4t'''
        model = model or cls
        return [
            f for f in model._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete
        ]

    @classmethod
    def get_all_field_names(cls, model=None):
        '''http://bit.ly/2aJ4Z4t'''
        model = model or cls
        return list(set(
            chain.from_iterable(
                (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)     # NOQA
                for field in model._meta.get_fields()
                if not (field.many_to_one and field.related_model is None)
        )))

    @classmethod
    def derived_models(cls):
        for i in cls._meta.related_objects:
            if all([
                isinstance(i, OneToOneRel),
                issubclass(i.related_model, cls._meta.model)
            ]):
                yield (i, i.related_model)

    @classmethod
    def cleanse_value(cls, key, value, model=None):
        model = model or cls
        try:
            if key not in model._meta.fields:
                return value
            field = model._meta.get_field(key)
            if isinstance(field, RelatedField):
                return value
            if isinstance(field, BooleanField):  # NOQA
                value = force_bool(value)
            return field.to_python(value)
        except:
            return None

    @classmethod
    def cleanse_values(cls, value_dict, model=None):
        model = model or cls

        return dict(
            (key, cls.cleanse_value(key, value))
            for key, value in value_dict.items())

    @classmethod
    def parse_perm(cls, perm):
        g = re.search(
            "(?P<app_label>[^\.]+).(?P<action>.+)_(?P<model>.+)",
            perm or '')
        return g and g.groupdict() or {}

    def has_perm(self, obj, perm):
        return False            # for safe

    @property
    def instance(self):
        '''actual model instance of subclass-ed model'''
        def _cache():
            self._instance = self
            for field, model in self.derived_models():
                self._instance = model.objects.filter(
                    **{field.field_name: self.id}).first()
                if self._instance:
                    break
            self._instance = self._instance or self
            return self._instance

        return getattr(self, '_instance', _cache())

    def to_dict(self, *excludes):
        res = model_to_dict(self)
        map(lambda k: res.pop(k, None), excludes)
        return res

    def to_json(self, **kwargs):
        return Sz.to_json(self, **kwargs)

    @classmethod
    def from_json(cls, jsonstr, **kwargs):
        data = Sz.load_json(jsonstr, **kwargs)
        return data
