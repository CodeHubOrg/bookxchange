from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=200, widget=forms.EmailInput(attrs={"class": "uk-input"})
    )
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "uk-input"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=("Password confirmation"),
        widget=forms.PasswordInput(attrs={"class": "uk-input"}),
        strip=False,
        help_text=("Enter the same password as before, for verification."),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "username", "password1", "password2")
        widgets = {"username": forms.TextInput(attrs={"class": "uk-input"})}


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
