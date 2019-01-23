from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.core.mail import send_mail, BadHeaderError
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .models import CustomUser
from .forms import CustomUserCreationForm
from .tokens import account_activation_token


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.save()
            current_site = get_current_site(request)
            subject = "Activate your Bookx account."
            message = render_to_string(
                "acc_activate_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(
                        force_bytes(user.pk)
                    ).decode(),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = [form.cleaned_data.get("email")]

            try:
                send_mail(subject, message, "info@codehub.org.uk", to_email)
                return HttpResponseRedirect(reverse("confirm_email"))
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

        return render(request, self.template_name, {"form": form})


class ConfirmEmail(TemplateView):
    template_name = "registration/confirmation_sent.html"


class ConfirmationComplete(TemplateView):
    template_name = "registration/confirmation_complete.html"


def parse_uid(uidb64):
    try:
        return int(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError):
        return None


def handle_activation_success(request, user):
    user.is_active = True
    user.save()
    login(request, user)


def activate(request, uidb64, token):
    uid = parse_uid(uidb64)
    if uid:
        user = CustomUser.objects.get(pk=uid)
        if user and account_activation_token.check_token(user, token):
            handle_activation_success(request, user)
        return HttpResponseRedirect(reverse("confirmation_complete"))
    else:
        return HttpResponse("Activation link is invalid!")
