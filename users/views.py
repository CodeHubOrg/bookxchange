from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views import generic
from django.core.mail import send_mail, BadHeaderError
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
            # import ipdb

            # ipdb.set_trace()
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
                return HttpResponse(
                    "Please confirm your email address to complete the registration"
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

        return render(request, self.template_name, {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account."
        )
    else:
        return HttpResponse("Activation link is invalid!")
