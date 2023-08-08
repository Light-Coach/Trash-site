from typing import Any, Dict
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    SetPasswordForm,
    PasswordResetForm,
)
from captcha.fields import CaptchaField
from tinymce.widgets import TinyMCE


class RegisterUserForm(UserCreationForm):
    captcha = CaptchaField()

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2", "captcha")

    def save(self, commit: bool = ...) -> Any:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class LoginUserForm(AuthenticationForm):
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Имя или email-адрес",
            }
        ),
        label="Имя или email-адрес",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль"}
        ),
        label="Пароль",
    )


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ("new_password1", "new_password2")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class ResetPasswordForm(PasswordResetForm):
    captcha = CaptchaField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

class NewsletterForm(forms.Form):
    subject = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема рассылки"}), label="")
    receivers = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), label="Адресаты получения писем")
    message = forms.CharField(widget=TinyMCE(), label="Содержание письма")

class FeedbackFormForAuthenticatedUsers(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput())
    email = forms.EmailField(widget=forms.HiddenInput())
    message = forms.CharField(
        min_length=20,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Сообщение",
                "cols": 30,
                "rows": 5,
                "class": "form-control",
            }
        ),
    )
    captcha = CaptchaField()


class FeedbackForm(forms.Form):
    name = forms.CharField(
        min_length=2,
        widget=forms.TextInput(
            attrs={"placeholder": "Ваше имя", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    message = forms.CharField(
        min_length=20,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Сообщение",
                "cols": 30,
                "rows": 5,
                "class": "form-control",
            }
        ),
    )
    captcha = CaptchaField()
