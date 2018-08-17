from django.urls import path
from . import views


urlpatterns = [
    path('hook/<str:app_key>', views.hook, name='corekit_bitbucket_hook'),                   
]
