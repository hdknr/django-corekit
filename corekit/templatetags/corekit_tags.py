from django import template
from django.utils.safestring import SafeText, mark_safe as _S
from django.utils.translation import ugettext_lazy as _
from corekit import serializers, utils


register = template.Library()



@register.filter
def jsonize(obj, class_name=None):
    if not obj:
        return 'null'
    return serializers.to_json(obj, class_name=class_name)


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


@register.filter
def gfm(text):
    '''Github Favored Markdown'''
    return utils.to_gfm(text)


@register.simple_tag(takes_context=True)
def admin_change_link(context, instance, label=None, private=False):
    if not instance:
        return ''
    label = label or str(instance)
    request = context.get('request', None) 
    if request and request.user.is_staff:
        if label == 'icon':
            label = _('Admin Change Link Icon')
        url = utils.to_admin_change_url(instance)
        return  _S(f'<a href="{url}">{label}</a>')
    return  private and '' or _S(label) 
