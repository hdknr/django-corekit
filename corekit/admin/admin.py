# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib import admin
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission, ContentType

from corekit import utils


def register(module_name, admins, ignore_models=[]):
    ''' Regiter Admin UI  
    
    admin.py::

        from corekit.admin import register
        register(__name__, globals(), ignore_models=['User', ])

    '''
    app_label = module_name.split('.')[-2:][0]
    for model in apps.get_app_config(app_label).get_models():

        if model.__name__ in ignore_models:
            continue
        name = "%sAdmin" % model.__name__
        admin_class = admins.get(name, None)
        if admin_class is None:
            admin_class = type(
                "%sAdmin" % model.__name__,
                (admin.ModelAdmin,), {},
            )

        if admin_class.list_display == ('__str__',):
            admin_class.list_display = tuple(
                [f.name for f in model._meta.fields])

        additionals = getattr(admin_class, 'list_additionals', ())
        excludes = getattr(admin_class, 'list_excludes', ())
        admin_class.list_display = tuple(
            [n for n in admin_class.list_display
             if n not in excludes]) + additionals

        admin.site.register(model, admin_class)


class NoneListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', _('None'), ),
            ('0', _('!= None'), ),
        )

    def queryset(self, request, queryset):
        if self.value() in ('0', '1'):
            kwargs = {
                '{0}__isnull'.format(self.parameter_name): self.value() == '1'
            }
            return queryset.filter(**kwargs)
        return queryset

    @classmethod
    def create(cls, title, parameter_name):
        return type(
            'NoneListFilterEx', (cls, ),
            {'title': title, 'parameter_name': parameter_name})


class CorelatedFilter(admin.RelatedFieldListFilter):

    def field_choices(self, field, request, model_admin):
        fk = getattr(self, 'fk', None)
        fk = fk and f'{fk}__' or ''
        name = f"{fk}{field.name}__{self.cofield}"
        covalue = request.GET.get(name, '')
        if not covalue:
            if getattr(self, 'show_all', True):
                return field.get_choices(include_blank=False)
            else:
                return []

        return field.get_choices(
            include_blank=False,
            limit_choices_to={self.cofield: covalue})


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_i18n', 'codename', 'content_type')
    list_filter = [
        # 'group',
        'content_type__app_label',
        ('content_type',
         type('', (CorelatedFilter,), {'cofield': 'app_label'})),
    ]
    search_fields = [
        'name', 'codename', 'content_type__app_label']
    readonly_fields = [
        'name', 'codename', 'content_type_link',
        'name_i18n', 'natural_key',
        'users_list', 'groups_list', ]
    exclude = ['content_type']

    def content_type_link(self, obj):
        ct = obj.content_type
        link = "admin:{}_{}_change".format(
            ct._meta.app_label, ct._meta.model_name)
        modellink = "admin:{}_{}_changelist".format(
            ct.app_label, ct.model)
        return utils.render(
            ''' <a href="{% url link ct.id %}">{{ ct }}</a>
                /<a href="{% url modellink %}">{{ name }}</a>
            ''',
            ct=ct, link=link,
            modellink=modellink, name=str(ct.model_class()))

    content_type_link.short_description = _('Model')
    content_type_link.allow_tags = True

    def name_i18n(self, obj):
        return _(obj.name)

    name_i18n.short_description = _('Name i18n')
    name_i18n.allow_tags = True

    def users_list(self, obj):
        return utils.render_by(
            'core/attr_queryset.html', instances=obj.user_set, is_admin=True)

    users_list.short_description = _('Users')
    users_list.allow_tags = True

    def groups_list(self, obj):
        return utils.render_by(
            'core/permission_groups.html', instances=obj.group_set,
            is_admin=True)

    groups_list.short_description = _('Groups')
    groups_list.allow_tags = True


class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model_name', 'model')
    list_filter = ['app_label', ]
    readonly_fields = ('app_label', 'model', 'model_link')

    def model_name(self, obj):
        mc = obj.model_class()
        return mc and mc._meta.verbose_name

    def model_link(self, obj):
        opt = obj.model_class()._meta
        link = "admin:{}_{}_changelist".format(opt.app_label, opt.model_name)
        return utils.render(
            ''' <a href="{% url link %}">{{ opt.verbose_name }}</a>''',
            opt=opt, link=link)

    model_link.short_description = _('Model')
    model_link.allow_tags = True

admin.site.register(Permission, PermissionAdmin)
admin.site.register(ContentType, ContentTypeAdmin)


class CoreAdmin(admin.ModelAdmin):

    def modify_form(self, form, request, obj=None, **kwargs):
        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super(CoreAdmin, self).get_form(request, obj=obj, **kwargs)
        return self.modify_form(form, request, obj=obj, **kwargs)
