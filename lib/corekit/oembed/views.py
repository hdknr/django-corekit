# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from corekit import views as core_views, methods
from corekit.utils import render_by
from logging import getLogger
import json
logger = getLogger()


class OembedView(core_views.View):

    def get_instance(self, content_type_key, id):
        return methods.CoreModel.contenttype_instance(content_type_key, id)

    @core_views.handler(
        url=r'^(?P<content_type>.+)/(?P<id>\d+)$',
        name="corekit_oembed_api", order=20, )
    def api(self, request, content_type, id):
        '''
        <link rel="alternate" type="application/json+oembed"
         href="{% fullurl 'corekit_oembed_api'
            content_type='blogs.article' id=instance.id %}" >
        '''
        instance = self.get_instance(content_type, id)
        if not instance:
            return self.page_not_found()

        template = "oembed/{}/oembed.json".format(content_type)
        default = json.loads(
            render_by(template, request=request, instance=instance))
        embed_html = "oembed/{}/embed.html".format(content_type)
        default['html'] = render_by(
            embed_html, request=request, instance=instance)
        return self.cors(self.json(default), origin='*')

    @core_views.handler(
        url=r'^(?P<content_type>.+)/(?P<id>\d+)/embed$',
        name="corekit_oembed_embed", order=20, )
    def embed(self, request, content_type, id):
        instance = self.get_instance(content_type, id)
        if not instance:
            return self.page_not_found()

        template = "oembed/{}/embed.html".format(content_type)
        return self.default_render(instance, template)

    @core_views.handler(
        url=r'^(?P<content_type>.+)/(?P<id>\d+)/widget$',
        name="corekit_oembed_widget", order=20, )
    def widget(self, request, content_type, id):
        instance = self.get_instance(content_type, id)
        if not instance:
            return self.page_not_found()

        template = "oembed/{}/widget.html".format(content_type)
        return self.default_render(instance, template)

    @core_views.handler(
        url=r'^(?P<content_type>.+)/(?P<id>\d+)/widget.js',
        name="corekit_oembed_script", order=20, )
    def script(self, request, content_type, id):
        instance = self.get_instance(content_type, id)
        if not instance:
            return self.page_not_found()

        template = "oembed/{}/widget.js".format(content_type)
        return self.default_render(
            instance, template,  'application/json; charset=utf-8')

    def default_render(self, instance, template, content_type=None):
        res = self.render(
            template, content_type=content_type, instance=instance)
        return self.cors(res, origin='*')
