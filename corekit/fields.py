# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils import six
from django.utils.encoding import force_text
from django.db import DEFAULT_DB_ALIAS


def get_m2m_value(field, field_value):
    # Handle M2M relations
    model = field.remote_field.model

    if hasattr(model._default_manager, 'get_by_natural_key'):
        def m2m_convert(value):
            if hasattr(value, '__iter__') and not isinstance(value, six.text_type):             # NOQA
                return model._default_manager.db_manager(db).get_by_natural_key(*value).pk      # NOQA
            else:
                return force_text(model._meta.pk.to_python(value), strings_only=True)           # NOQA
    else:
        def m2m_convert(v):
            return force_text(model._meta.pk.to_python(v), strings_only=True)

    try:
        m2m_data = []
        for pk in field_value:
            m2m_data.append(m2m_convert(pk))
        return m2m_data
    except Exception as e:
        raise e


def get_fk_value(field, field_value, db=None):
    db = db or DEFAULT_DB_ALIAS
    # Handle FK fields
    if not field_value:
        return None

    model = field.remote_field.model
    try:
        default_manager = model._default_manager
        field_name = field.remote_field.field_name

        if hasattr(default_manager, 'get_by_natural_key'):
            if hasattr(field_value, '__iter__') and not isinstance(field_value, six.text_type):     # NOQA
                obj = default_manager.db_manager(db).get_by_natural_key(*field_value)               # NOQA
                value = getattr(obj, field.remote_field.field_name)
                # If this is a natural foreign key to an object that
                # has a FK/O2O as the foreign key, use the FK value
                if model._meta.pk.remote_field:
                    value = value.pk
                return value
            else:
                return model._meta.get_field(field_name).to_python(field_value)    # NOQA
            return value
        else:
            return model._meta.get_field(field_name).to_python(field_value)    # NOQA
    except Exception as e:
        raise e


def get_value(field, field_value):
    return field.to_python(field_value)


def get_field_value(field, field_value, encoding='utf-8'):
    '''return (1 if m2m else 0, returning_value)'''

    if isinstance(field_value, str):
        field_value = force_text(field_value, encoding, strings_only=True)

    if field.remote_field and isinstance(field.remote_field, models.ManyToManyRel):     # NOQA
        return (1, get_m2m_value(field, field_value))
    elif field.remote_field and isinstance(field.remote_field, models.ManyToOneRel):    # NOQA
        return (0, get_fk_value(field, field_value))
    else:
        return (0, get_value(field, field_value))
