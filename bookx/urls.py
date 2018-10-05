"""bookx URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('admin/', admin.site.urls),   
    path('books/', views.book_list, name='book_list'),
    path('book/new', views.book_new, name='book_new'),
    url(r'^book/(?P<pk>\d+)/$', views.book, name='book_detail'),
     # url(r'^(?P<username>[\w.@+-]+)/$', views.user_profile, name='user_profile'),
    url(r'^signup/$', core_views.signup, name='signup'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    