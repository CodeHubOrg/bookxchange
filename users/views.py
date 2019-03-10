from django.db.models import Max
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import BadHeaderError
from django.views import generic
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth import login

from django.utils.http import urlsafe_base64_decode

from .models import CustomUser
from .forms import CustomUserCreationForm
from .tokens import account_activation_token
from .email_notifications import send_account_confirmation
from books.models import Book, BookHolder


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
            to_email = [form.cleaned_data.get("email")]
            try:
                send_account_confirmation(request, user, to_email)
                return HttpResponseRedirect(reverse("confirm_email"))
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

        return render(request, self.template_name, {"form": form})


class ConfirmEmail(TemplateView):
    template_name = "registration/confirmation_sent.html"


class ConfirmationComplete(TemplateView):
    template_name = "registration/confirmation_complete.html"


def get_books_borrowed(user):
    q0 = (
        BookHolder.objects.select_related("book")
        .filter(book__status="OL")
        .exclude(date_borrowed=None)
    )
    q1 = (
        q0.filter(holder__id=user.id)
        .values("book__title", "book__thumb", "book__owner__username")
        .annotate(max_date=Max("date_borrowed"))
        .order_by("book__title", "max_date")
    )
    q2 = (
        q0.values("book__title", "book__thumb", "book__owner__username")
        .annotate(max_date=Max("date_borrowed"))
        .order_by("book__title", "max_date")
    )
    return q1.intersection(q2)


def get_own_books_on_loan(user):
    return (
        BookHolder.objects.select_related("book")
        .filter(book__status="OL", book__owner__id=user.id)
        .exclude(date_borrowed=None)
        .values("book__title", "book__thumb")
        .annotate(
            max_date=Max("date_borrowed"), borrowed_by=Max("holder__username")
        )
        .order_by("book__title", "max_date")
    )


class UserProfile(TemplateView):
    template_name = "profile.html"

    def get(self, request):
        borrowed = get_books_borrowed(request.user)
        lending = get_own_books_on_loan(request.user)
        return render(
            request,
            self.template_name,
            {"borrowed": borrowed, "lending": lending},
        )


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
