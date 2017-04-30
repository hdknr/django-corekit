from django.conf.urls import url
from . import views

'''
Search:

    <a href="{% url 'doc_search' %}?q=your_word">Search your_word</a>
'''

urlpatterns = [
    url(r'search.html',
        views.protected, name="docs_search", kwargs={'path': 'search.html'}),
    url(r'(?P<module>.+)/(?P<entry>.+).help$', views.help, name="docs_help"),
    url(r'(?P<path>.*)', views.protected, name="docs_publish"),
    url(r'', views.protected, name="docs_home", kwargs={'path': ''}),
]
