# encoding: utf-8
from django.forms.models import model_to_dict
from django.db.models import Model
from django.core.files import File
from django.db.models.fields.files import FieldFile
from rest_framework import serializers, relations, fields as rest_fields
from datetime import datetime
from enum import Enum
from corekit import utils
from decimal import Decimal
import json
import yaml


from collections import OrderedDict


class BaseModelSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values()
                  if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            # except SkipField:
            except:
                continue

            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation is None:
                    # Do not seralize empty objects
                    continue
                if isinstance(represenation, list) and not represenation:
                    # Do not serialize empty lists
                    continue
                ret[field.field_name] = represenation

        return ret

    def dump(self):
        return BaseModelSerializer.to_json(self.data)


class ExportModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.verbose_field = kwargs.pop('verbose_field', True)
        super(ExportModelSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        '''(override)'''
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            # translated field names
            if self.verbose_field:
                name = u"{}".format(self.Meta.model._meta.get_field(
                    field.field_name).verbose_name)
            else:
                name = field.field_name
            try:
                attribute = field.get_attribute(instance)
            except rest_fields.SkipField:
                continue

            check_for_none = \
                attribute.pk if isinstance(attribute, relations.PKOnlyObject) \
                else attribute      # NOQA

            if check_for_none is None:
                ret[name] = ''
            else:
                val = field.to_representation(attribute)
                ret[name] = '' if val is None else val

        return ret


class BaseObjectSerializer(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, Model):
            return model_to_dict(obj)
        if isinstance(obj, FieldFile):
            return {'url': obj.url, 'name': obj.name}
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, object):
            ex = obj._excludes if hasattr(obj, '_excludes') else {}
            vals = obj._customes.copy() if hasattr(obj, '_customs') else {}
            vals.update(getattr(obj, '__dict__', {}))
            return dict([(k, v) for k, v in vals.items()
                         if k not in ex and not k.startswith('_') and v])
        return super(BaseObjectSerializer, self).default(obj)

    @classmethod
    def to_json(cls, obj, *args, **kwargs):
        return json.dumps(obj, cls=cls, *args, **kwargs)

    @classmethod
    def to_json_file(cls, obj, name=None, *args, **kwargs):
        name = name or u"{}.json".format(cls.__name__)
        return File(
            utils.contents(cls.to_json(obj, *args, **kwargs)), name=name)

    @classmethod
    def load_json(cls, jsonstr,  *args, **kwargs):
        return json.loads(jsonstr, *args, **kwargs)

    @classmethod
    def to_yaml(cls, obj, *args, **kwargs):
        return yaml.safe_dump(obj, *args, **kwargs)

    @classmethod
    def to_dict(cls, obj, *args, **kwargs):
        return json.loads(cls.to_json(obj, *args, **kwargs))
