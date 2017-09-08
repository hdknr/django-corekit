# coding: utf-8
from django.db import models
from .archives import ModelZipball
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CoreQuerySet(models.QuerySet):

    def zipball(self, stream):
        ball = ModelZipball()
        ball.append_query(self.filter())
        ball.writeto(stream)

    def page(self, items=30, page=1):
        ''' Page objects'''
        paginator = Paginator(self, items)
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            return paginator.page(1)
        except EmptyPage:
            # If page is out of range
            # (e.g. 9999), deliver last
            # page of results.
            return paginator.page(paginator.num_pages)
