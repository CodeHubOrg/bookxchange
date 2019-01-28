from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("confirm_email", views.ConfirmEmail.as_view(), name="confirm_email"),
    path(
        "confirmation_complete",
        views.ConfirmationComplete.as_view(),
        name="confirmation_complete",
    ),
    path(
        "activate/<slug:uidb64>/<slug:token>", views.activate, name="activate"
    ),
]
