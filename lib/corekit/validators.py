# coding: utf-8
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


def validate_least1(value):
    if value < 1:
        raise ValidationError(_('Value MUST be more than 1'))


zipcode_validators = [
    RegexValidator(regex=r'^\d{7}$', message=_('Zipcode is 7 digits'))]
