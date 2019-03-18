from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


def get_admin_urlname(instance_or_class, view='change'):
    opt = instance_or_class._meta
    return f"admin:{opt.app_label}_{opt.model_name}_{view}"


def get_admin_url(instance_or_class, view='change', id=None):
    id = id or getattr(instance_or_class, 'id', None)
    return reverse(
        get_admin_urlname(instance_or_class, view=view), args=[id])
