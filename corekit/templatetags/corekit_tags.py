from django import template
from corekit import serializers

register = template.Library()


@register.simple_tag(takes_context=True)
def to_json(context, obj, class_name=None):
    '''Convert an object to JSON using Serializer'''
    if not obj:
        return 'null'
    return serializers.to_json(
        obj, class_name=class_name, request=context.get('request', None))