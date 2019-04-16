from django.urls import path, re_path
from . import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("confirm_email", views.ConfirmEmail.as_view(), name="confirm_email"),
    path(
        "confirmation_complete",
        views.ConfirmationComplete.as_view(),
        name="confirmation_complete",
    ),
    re_path(
        r"^emaillogin/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.emaillogin,
        name="emaillogin",
    ),
    re_path(
        r"^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.activate,
        name="activate",
    ),
    path("profile/", views.UserProfile.as_view(), name="profile"),
]
