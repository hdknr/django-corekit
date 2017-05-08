# coding: utf-8
''' http://oembed.com/ '''
from corekit import utils
from django.http.request import QueryDict
import requests


def twitter_embed_html(url):
    return requests.get(
        'https://publish.twitter.com/oembed', params={'url': url}
    ).json().get('html', '')


def instagram_embed_html(url):
    uo = utils.url(url)
    return utils.render(
        '''<iframe src="//instagram.com{{ uo.path }}embed/"
        width="612" height="710" frameborder="0"
        scrolling="no" allowtransparency="true"></iframe>''',
        uo=uo)


def youtube_embed_html(url):
    uo = utils.url(url)
    q = QueryDict(uo.query)
    return utils.render(
        '''<iframe width="560" height="315"
        src="https://www.youtube.com/embed/{{ q.v }}"
        frameborder="0" allowfullscreen></iframe>''',
        q=q)


def get_html(url):
    uo = utils.url(url)
    return {
        'twitter.com': twitter_embed_html,
        'www.instagram.com': instagram_embed_html,
        'www.youtube.com': youtube_embed_html,
    }.get(uo.netloc, lambda o: '')(url)
