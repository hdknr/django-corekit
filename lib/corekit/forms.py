# -*- coding: utf-8 -*-
from django import forms


class PreviewMixin(object):
    def to_preview(self):
        ''' covnert all fields in hidde fields'''
        for k, f in self.fields.items():
            if str(type(f)).find('Multi') > 0:
                f.widget = forms.MultipleHiddenInput()
            else:
                f.widget = forms.HiddenInput()


def dynamic_modelform(data, instance, *args, **kwargs):
    '''create dynamic model form'''
    model_class = instance._meta.model
    meta = type(
        'Meta', (object, ),
        dict(
            exclude=[],
            model=model_class,
        )
    )
    fields = {}
    fields['__module__'] = model_class.__module__
    fields['Meta'] = meta

    return type(
        model_class._meta.object_name + "Form",
        (forms.ModelForm, ), fields)(data, instance=instance, *args, **kwargs)


class ChildrenFormSet(forms.BaseInlineFormSet):
    FORM_CLASS = None

    @classmethod
    def factory(cls, data, parent, extra=1, files=None, construct={}, **kwargs):
        formset_class = cls.create_class(
            parent._meta.concrete_model, extra=extra, **construct)
        return formset_class(data, files or None, instance=parent, **kwargs)

    @classmethod
    def create_class(cls, parent_class, extra=1, **kwargs):
        # https://docs.djangoproject.com/en/1.10/ref/forms/models/#inlineformset-factory
        return forms.inlineformset_factory(
            parent_class, cls.FORM_CLASS.Meta.model, form=cls.FORM_CLASS,
            extra=extra, formset=cls, **kwargs)


class ModelFormSet(forms.BaseModelFormSet):
    FORM_CLASS = None

    @classmethod
    def create_class(cls, extra=1, **kwargs):
        # https://docs.djangoproject.com/en/1.11/ref/forms/models/#modelformset-factory
        return forms.modelformset_factory(
            cls.FORM_CLASS.Meta.model, form=cls.FORM_CLASS,
            extra=extra, formset=cls, **kwargs)

    @classmethod
    def factory(
        cls, data, queryset=None, files=None, extra=1, construct={},
        **kwargs
    ):
        formset_class = cls.create_class(extra=extra, **construct)
        return formset_class(
            data or None, files or None, queryset=queryset, **kwargs)
