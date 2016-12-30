# coding: utf-8
from django.db import models
from .archives import ModelZipball


class CoreQuerySet(models.QuerySet):

    def zipball(self, stream):
        ball = ModelZipball()
        ball.append_query(self.filter())
        ball.writeto(stream)
