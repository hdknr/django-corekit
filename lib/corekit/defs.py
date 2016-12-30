# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .validators import zipcode_validators


class CoreModel(models.Model):

    ordinal = models.IntegerField(
        _(u'Ordinal'), help_text=_('Ordinal Help'), default=0)
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True)

    class Meta:
        abstract = True

WEEKDAY = [
    _('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'),
    _('Thursday'), _('Friday'), _('Saturday')]
WEEKDAY_CHOICES = tuple((WEEKDAY.index(i), i) for i in WEEKDAY)

MONTH_CHOICES = tuple((i, u"{:02d}月".format(i)) for i in range(1, 13))


def year_choices(years, from_year=None):
    from_year = from_year or timezone.now().year
    return tuple(
        (i, u"{:04d}年".format(i))
        for i in range(from_year, from_year + years))

PREFECTURES = [
    u"北海道",
    u"青森県", u"岩手県", u"宮城県", u"秋田県", u"山形県", u"福島県",
    u"茨城県", u"栃木県", u"群馬県", u"埼玉県", u"千葉県", u"東京都",
    u"神奈川県",
    u"新潟県", u"富山県", u"石川県", u"福井県",
    u"山梨県", u"長野県",
    u"岐阜県", u"静岡県", u"愛知県", u"三重県", u"滋賀県", u"京都府",
    u"大阪府", u"兵庫県", u"奈良県", u"和歌山県",
    u"鳥取県", u"島根県", u"岡山県", u"広島県", u"山口県",
    u"徳島県", u"香川県", u"愛媛県", u"高知県",
    u"福岡県", u"佐賀県", u"長崎県", u"熊本県", u"大分県", u"宮崎県",
    u"鹿児島県",
    u"沖縄県",
]

PREFECTURE_CHOICES = (
    ('', _(u'PREFECTURE_EMPTY')), ) + tuple([(p, p) for p in PREFECTURES])


class Posttal(models.Model):
    # [5, 5, 7, 18, 57, 185, 12, 30, 111, 1, 1, 1, 1, 1, 1]
    pass
    # code,
    # zip5
    # zip
    # prefecture_kana
    # city_kana
    # town_kana
    # prefecture
    # city
    # town
    # is_multi_zip
    # is_koaza
    # is_choume
    # is_share_zip
    # update_type
    # update_reason


class Address(models.Model):

    zipcode = models.CharField(
        _('Zip Code'), max_length=7, validators=zipcode_validators)
    prefecture = models.CharField(
        _('Prefecture'),
        choices=PREFECTURE_CHOICES, max_length=20)
    city = models.CharField(
        _('City'), max_length=20)
    address = models.CharField(
        _('Address'), max_length=100)
    building = models.CharField(
        _('Building'), max_length=50,
        null=True, default=None, blank=True)

    class Meta:
        abstract = True

    @property
    def full_address(self):
        return u"〒{}{}{}{}{}".format(
            self.zipcode, self.prefecture, self.city, self.address,
            self.building or '')
