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
    def factory(cls, data, parent, extra=1, **kwargs):
        formset_class = cls.create_class(
            parent._meta.concrete_model, extra=extra)
        return formset_class(data, instance=parent, **kwargs)

    @classmethod
    def create_class(cls, parent_class, extra=1):
        # https://docs.djangoproject.com/en/1.10/ref/forms/models/#inlineformset-factory
        return forms.inlineformset_factory(
            parent_class, cls.FORM_CLASS.Meta.model, form=cls.FORM_CLASS,
            extra=extra, formset=cls)
