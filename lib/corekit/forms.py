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
