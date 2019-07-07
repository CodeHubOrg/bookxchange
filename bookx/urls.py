from django.views.generic.base import RedirectView
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bookx import views


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="book_supercategory"), name="home", kwargs={"supercategory":"programming"}),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("books/", include("books.urls")),
    path("messages/", include("lending.urls")),
    path("users/", include("users.urls")),  # new
    path("users/", include("django.contrib.auth.urls")),  # new
    path("admin/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG is True:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
