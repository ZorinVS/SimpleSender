from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm

from mailings.forms import StyleFormMixin
from users.models import User


class RegisterUserCreationForm(StyleFormMixin, UserCreationForm):
    FIELDS_WITH_ATTRIBUTES = {
        "email": {"placeholder": "Введите email"},
        "phone_number": {"placeholder": "Формат: +7 999 666 33 33"},
        "country": {"placeholder": "Введите страну"},
    }

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите пароль"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Повторите пароль"}),
    )

    class Meta:
        model = User
        fields = ["email", "avatar", "phone_number", "country", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите email",
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].label = "Пароль"
        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Введите пароль",
        })


class UserForm(StyleFormMixin, forms.ModelForm):
    FIELDS_WITH_ATTRIBUTES = {
        "phone_number": {"class": "form-control", "placeholder": "Формат: +7 999 666 33 33"},
        "country": {"class": "form-control", "placeholder": "Введите страну"},
    }

    class Meta:
        model = User
        fields = ["avatar", "phone_number", "country"]


class PasswordResetForm(BasePasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )


class SetPasswordForm(BaseSetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите новый пароль"}),
        min_length=8,
        help_text="Пароль должен содержать хотя бы 8 символов",
    )

    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Повторно введите новый пароль"}),
        min_length=8,
    )
