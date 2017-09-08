# -*- coding: utf-8 -*-
from django import template
register = template.Library()


@register.simple_tag(takes_context=False)
def platform(model):
    import platform
    return platform
