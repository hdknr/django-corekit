from django import template
from django.utils.safestring import SafeText, mark_safe as _S
from corekit import serializers, utils
from django.template import Context

register = template.Library()


@register.simple_tag(takes_context=True)
def to_json(context, obj, class_name=None):
    '''Convert an object to JSON using Serializer'''
    if not obj:
        return 'null'
    return serializers.to_json(
        obj, class_name=class_name, request=context.get('request', None))


@register.simple_tag
def render_by(name, request=None, **ctx):
    t = template.loader.get_template(name)
    if utils.is_filetype(name, 'text/markdown'):
        t = template.Template(utils.to_gfm(t.template.source))
    return _S(t.render(Context(ctx)))