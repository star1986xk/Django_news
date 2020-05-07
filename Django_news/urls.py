"""Django_news URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^list/$', views.newsListAPI.as_view({'get': 'list'})),
    url(r'^info/$',
        views.newsInfoAPI.as_view({'get': 'get', 'post': 'create', 'patch': 'partial_update', 'delete': 'destroy'})),
    url(r'^search/$', views.searchAPI.as_view({'get': 'list','post': 'start','patch': 'end'})),
]
