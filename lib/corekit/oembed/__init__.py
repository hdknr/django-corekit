# coding: utf-8
from django.utils.http import urlquote
from django.core.cache import cache
from bs4 import BeautifulSoup as Soup
import requests
import re

TWITTER = "https://publish.twitter.com/oembed?url={url}"
INSTAGRAM = "https://api.instagram.com/oembed/?url={url}"
YOUTUBE = "http://www.youtube.com/oembed?url={url}&format=json"


PATTERN = [
    (r'(?P<scheme>https)\://(?P<host>www.youtube.com)(?P<path>/watch.+)', YOUTUBE),   # NOQA
    (r'(?P<scheme>https)\://(?P<host>www.instagram.com)(?P<path>/p/.+/)$', INSTAGRAM),  # NOQA
    (r'(?P<scheme>https)\://(?P<host>twitter.com)(?P<path>.+)$', TWITTER),
]


def find_url(url):
    res = requests.get(url)
    if res and res.status_code == 200 \
            and res.headers.get('Content-Type', '').startswith('text/html'):
        soup = Soup(res.text, 'html.parser')
        items = soup and soup.select('link[type="application/json+oembed"]')
        return items and items[0].attrs['href']


def get_url(url):
    for pattern in PATTERN:
        match = re.search(pattern[0], url)
        if match:
            return pattern[1].format(url=urlquote(url), **match.groupdict())
    return find_url(url)


def get_html(url):
    html = cache.get("oembed:" + url)
    if not html:
        html = requests.get(get_url(url)).json().get('html', None)
        cache.set("oembed:" + url, html)
    return html
