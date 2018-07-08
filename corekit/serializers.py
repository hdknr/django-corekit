from django.db import models
from django.utils.module_loading import import_string
from django.contrib.sites.models import Site
from rest_framework import serializers, relations, fields as rest_fields
from collections import OrderedDict
from . import encoders


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


class BaseObjectSerializer(encoders.JSONEncoder):
    pass


def to_json(obj, class_name=None, request=None):
    '''Convert an object to JSON'''
    if isinstance(obj, dict):
        return encoders.to_json(obj)

    ser = class_name and import_string(class_name)
    if ser:
        context = dict(request=request,)
        obj = ser(
            obj, context=context, many=isinstance(obj, (list, models.QuerySet))
        ).data
    return encoders.to_json(obj)