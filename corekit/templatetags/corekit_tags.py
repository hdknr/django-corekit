from django import template
from django.utils.safestring import SafeText, mark_safe as _S
from corekit import serializers, utils


register = template.Library()


@register.simple_tag(takes_context=True)
def to_json(context, obj, class_name=None):
    '''Convert an object to JSON using Serializer'''
    if not obj:
        return 'null'
    return serializers.to_json(
        obj, class_name=class_name, request=context.get('request', None))


@register.simple_tag
def render_by(name, **ctx):
    request = ctx.pop('request', None)
    t = template.loader.get_template(name)
    if utils.is_filetype(name, 'text/markdown'):
        t = template.engines['django'].from_string(utils.to_gfm(t.template.source)) 
    return _S(t.render(ctx, request=request))