# -*- coding: utf-8 -*-
from django import template, forms
from django.apps import registry
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, Manager, QuerySet, ImageField
from django.http.request import QueryDict
from django.middleware.csrf import get_token
from django.template import Context, Template, loader
from django.utils import formats
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe as _S
from django.utils.translation import ugettext_lazy as _
from corekit import (utils, methods, oembed as oe)
from datetime import date
import json
import os

register = template.Library()


@register.assignment_tag(takes_context=True)
def media_path(context, bulletin):
    return SafeText('media path')


@register.simple_tag(takes_context=True)
def ordering(context, field, key='o', default='asc'):
    '''
    {% load corekits %}
    <style>
    .sort-asc:after{content: "Down"}
    .sort-desc:after{content: "Up"}
    </style>

    <th>
    {% ordering 'id' as id_order %}
        <a href="?{{ id_order.query }}"> No.</a>
        <i class="sort-{{ id_order.direction }}"></i>
    </th>
    '''
    res = context.get('request').GET.copy()
    q = res.getlist(key)
    rfield = '-' + field
    if rfield in q:
        q.remove(rfield)
        direction = "asc"
    elif field in q:
        q.remove(field)
        direction = "desc"
    else:
        direction = 'desc' if default == 'asc' else 'asc'

    q = [field if direction == 'asc' else rfield] + q

    res.setlist(key, q)
    return dict(query=res.urlencode(), direction=direction)


@register.simple_tag(takes_context=False)
def filtering(queryset, **kwargs):
    # TODO: security considering
    return queryset.filter(**kwargs)


@register.simple_tag(takes_context=True)
def set_query(context, field, value):
    qdict = context.get('request').GET.copy()
    qdict.setlist(field, [value])
    return qdict.urlencode()


@register.filter
def has_val(value, key):
    return True


@register.filter
def tup(src, arg):
    ''' return tuple(src,args)'''
    if isinstance(src, tuple):
        return src + (arg, )
    return (src, arg, )


@register.filter
def has_perm((obj, user), perm):
    '''
        {% if org|tup:request.user|has_perm:"events.change_event" %}
            <a href="{{ add_url }}">{% trans "Add" %}</a>
        {% endif %}
    '''
    return user.has_perm(perm, obj)


@register.filter
def get_instance(id, content_type):
    return id and methods.CoreModel.contenttype_instance(content_type, id)


@register.filter
def get_instance_list(id_list, content_type):
    model = methods.CoreModel.contenttype_model(content_type)
    return model.objects.filter(id__in=id_list)


@register.filter
def can((obj, user), action):
    '''
        {% if org|tup:request.user|can:"events.change_event" %}
            <a href="{{ add_url }}">{% trans "Add" %}</a>
        {% endif %}
    '''
    perm = utils.get_perm_name(obj, action)
    return user.has_perm(perm, obj)


@register.filter
def typename(obj):
    return obj.__class__.__name__


@register.filter
def attr(instance, name):

    if isinstance(instance, (forms.Form, forms.ModelForm)):
        res = name in instance.fields and instance[name]
        return res

    if hasattr(instance, 'cleaned_data'):
        res = instance.cleaned_data.get(name, '') or ''
        if isinstance(res, QuerySet):
            return render_by('corekit/attr_queryset.html', instances=res)
        return res

    value = getattr(instance, name, '') or ''

    if isinstance(value, bool):
        return value and _(u'Yes') or _(u'No')

    if isinstance(value, Manager) and \
            instance._meta.get_field(name).many_to_many:
        # ManyToManyField
        return render_by('corekit/attr_queryset.html', instances=value)

    if isinstance(value, ImageField):
        return render_by('corekit/attr_image.html', instances=value)

    return value


@register.filter
def gfm(text):
    '''Github Favored Markdown'''
    return utils.to_gfm(text)


@register.filter
def js(obj):
    return SafeText(json.dumps(obj, cls=DjangoJSONEncoder))


@register.filter(name='get')
def get(o, index):
    try:
        return o[index]
    except:
        return settings.TEMPLATE_STRING_IF_INVALID


@register.filter(name='getattr')
def getattrfilter(o, attr):
    try:
        return getattr(o, attr)
    except:
        return settings.TEMPLATE_STRING_IF_INVALID


@register.filter
def to_admin_change_url(instance):
    try:
        return instance and utils.to_admin_change_url(instance) or ''
    except:
        pass


@register.simple_tag(takes_context=True)
def bs_form_group(context, *fields, **kwargs):
    name = 'name' in kwargs and kwargs.pop('name') or 'core/form_group.html'
    t = context.template.engine.get_template(name)
    kwargs['fields'] = fields
    kwargs['errors'] = [f.errors for f in fields if f.errors]
    kwargs['label'] = kwargs.get('label', None) or fields[0].label
    kwargs['readonly'] = kwargs.get('readonly', False)
    widths = [int(i) for i in kwargs.get('widths', '2,2,2,2,2').split(',')]
    for i in range(len(fields)):
        fields[i].column_width = widths[i]
    return t.render(Context(kwargs, autoescape=context.autoescape))


@register.filter
def app_config(obj):
    if isinstance(obj, basestring):
        return registry.apps.get_app_config(obj)
    return registry.apps.get_app_config(getattr(obj, 'app_label', ''))


def render(src, **ctx):
    return _S(Template(src).render(Context(ctx)))


def render_by(name, **ctx):
    return _S(loader.get_template(name).render(Context(ctx)))


@register.filter
def as_value(bf):
    ''' bound field as value'''
    res = bf.value()

    if isinstance(bf.field, forms.BooleanField):
        return res == 'on' and _('Yes') or _('No')

    if not res:
        return res

    if isinstance(res, date):
        return formats.date_format(res, "Y-m-d (D)")

    val = getattr(bf.form.instance, bf.name, None)
    if val and isinstance(val, Model):
        if hasattr(val, 'get_absolute_url'):
            try:
                return render('''
                <a href="{{ i.get_absolute_url }}">{{ i }}</a>''', i=val)
            except:
                pass
        return val

    if hasattr(bf.field, 'choices'):
        return dict((u"{}".format(k), v) for k, v in bf.field.choices)[res]

    return res


@register.filter
def basename(path):
    return os.path.basename(path)


@register.filter
def extname(path):
    name, ext = os.path.splitext(path)
    return ext.replace('.', '')


@register.simple_tag
def qfilter(qs, **kwargs):
    return qs.filter(**kwargs)


@register.simple_tag(takes_context=True)
def dbtemplate_admin(context, name, label, css_class=""):
    if not context['request'].user.is_staff:
        return ""
    from dbtemplates.models import Template
    t = Template.objects.filter(name=name).first()
    if not t:
        return ''
    return render_by(
        'corekit/dbtemplate_admin.html',
        url=methods.CoreModel().admin_change_url(t),
        css_class=css_class, label=label)


@register.filter
def full_name(user):
    if user.first_name and user.last_name:
        return u" ".join([user.last_name, user.first_name])
    return user.username


@register.filter
def csrf_tag(request):
    csrf_token = get_token(request)
    return format_html(
        "<input type='hidden' name='csrfmiddlewaretoken' value='{}' />",
        csrf_token)


@register.simple_tag(takes_context=False)
def get_fields(model):
    '''model fields dict(key=naem, value=Field object'''
    return methods.CoreModel.get_all_fields(model=model)


@register.simple_tag(takes_context=True)
def inject(context, source):
    ''' Inject Template source string'''
    head = "{% load i18n humanize static %}"
    templ = Template(head + source)
    return templ.render(context)


@register.simple_tag
def object_from(name):
    '''テンプレートソース(JSON, YAML)をオブジェクトに変換'''
    source = utils.load_template(name)
    format = os.path.splitext(name)[1].replace('.', '')
    return utils.convert(source, format=format)


@register.simple_tag(takes_context=False)
def assign(value):
    '''変数として設定するために値を返す'''
    return value


@register.simple_tag(takes_context=False)
def oembed(url):
    '''oEmbed HTML を返す'''
    return _S(oe.get_html(url).get('html'))


@register.simple_tag
def gmap(address, lat=None, lng=None, template='corekit/gmap.html'):
    '''Google Map'''
    param = dict(q=address,)
    qd = QueryDict(mutable=True)
    qd.update(param)
    return utils.render_by(template, gmap=qd, lat=lat, lng=lng)


@register.simple_tag
def in_pager_range(page, width=7):
    r = page.paginator.page_range
    if width not in r:
        return list(r)
    res = range(1, width + 1) \
        + range(page.number - (width - 1) / 2, page.number + width - 1) \
        + range(r[-width] / 2, r[-width] / 2 + width) \
        + range(r[-width], r[-width] + width)
    return res
