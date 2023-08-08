from typing import Any, Dict, Optional
from django.db import models
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from users.models import SubscribedUsers
from trash_app.utils import ContextDataMenu
from users.decorators import *
from users.forms import *
from users.tokens import account_activation_token

# Create your views here.


def email_activate(request, user, to_email):
    """Функция для формирования активации аккаунта по email-адресу"""

    mail_subject = "Активируйте свой аккаунт."
    message = render_to_string(
        "authenticate_and_change/template_activate_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f'{user}, чтобы завершить регистрацию проверьте почту - {to_email} \
                    и подтвердите нажатием на активационную ссылку. Возможно потребуется проверить папку "Спам"',
        )
    else:
        messages.error(
            request,
            f"Возникла проблема при отправке письма на адрес {to_email}, проверьте правильность введённого адреса.",
        )


def activate(request, uidb64, token):
    """Функция для обработки ссылки-подтверждения аккаунта"""

    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f"Email подтверждён. Можете войти в аккаунт.")
        return redirect("login")
    else:
        messages.error(request, f"Активационная ссылка не действительна")

    return redirect("from_start")


@user_is_not_authenticated
def register(request):
    """Функция для регистрации пользователя"""

    context = {"title": "Регистрация", "menu": ContextDataMenu}

    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            email_activate(request, user, form.cleaned_data.get("email"))
            return redirect("from_start")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = RegisterUserForm()

    context["form"] = form

    return render(request=request, template_name="users/register.html", context=context)


def profile(request, username):
    """Функция для редактирования профиля пользователя"""

    context = {"title": "Информация субъекта", "menu": ContextDataMenu}

    if request.method == "POST":
        user = request.user
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f"{user_form}, профиль обновлён")
            return redirect("from_start")

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_object_or_404(get_user_model(), username=username)
    context["user"] = user
    form = EditProfileForm(instance=user)
    context["form"] = form
    return render(request, "users/profile.html", context=context)


@login_required
def password_change(request):
    """Функция для смены пароля"""

    context = {"title": "Смена пароля", "menu": ContextDataMenu}

    user = request.user
    form = ChangePasswordForm(user)
    if request.method == "POST":
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш пароль изменён.")
            return redirect("login")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    context["form"] = form
    return render(
        request, "authenticate_and_change/password_reset_confirm.html", context=context
    )


@user_is_not_authenticated
def password_reset_request(request):
    """Функция для запроса на изменение пароля в случае забытия оного"""

    context = {"title": "Сброс пароля", "menu": ContextDataMenu}

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            associated_user = (
                get_user_model().objects.filter(Q(email=user_email)).first()
            )
            if associated_user:
                subject = "Запрос сброса пароля."
                message = render_to_string(
                    "authenticate_and_change/template_reset_password.html",
                    {
                        "user": associated_user,
                        "domain": get_current_site(request).domain,
                        "uid": urlsafe_base64_encode(force_bytes(associated_user.pk)),
                        "token": account_activation_token.make_token(associated_user),
                        "protocol": "https" if request.is_secure() else "http",
                    },
                )
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(
                        request,
                        """
                        <h2>Сброс пароля исполнен.</h2><hr>
                        <p>
                            Мы отправили вам инструкции для изменения пароля на почту. Если вы не видите письма, проверьте папку "Спам".
                        </p>
                        """,
                    )
                else:
                    messages.error(
                        request, "Проблема при отправке письма о сбросе пароля"
                    )
            return redirect("from_start")

        for key, error in list(form.errors.items()):
            if key == "captcha" and error[0] == "This field is required.":
                messages.error(request, "Необходимо ввести верные символы в CAPTCHA")
                continue

    form = ResetPasswordForm()
    context["form"] = form
    return render(
        request,
        template_name="authenticate_and_change/password_reset.html",
        context=context,
    )


def password_reset_confirm(request, uidb64, token):
    """Функция подтверждения сброса пароля"""

    context = {"title": "Подтверждение сброса пароля", "menu": ContextDataMenu}
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Ваш пароль установлен. Можете авторизоваться."
                )
                return redirect("from_start")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = ChangePasswordForm(user)
        context["form"] = form
        return render(
            request,
            "authenticate_and_change/password_reset_confirm.html",
            context=context,
        )
    else:
        messages.error(request, "Ссылка устарела")

    messages.error(request, "Что-то пошло не так...")
    return redirect("from_start")


@user_is_not_authenticated
def custom_login(request):
    """Функция для авторизации"""

    context = {"title": "Авторизация", "menu": ContextDataMenu}

    if request.method == "POST":
        form = LoginUserForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"А, вы пришли.")
                return redirect(request.GET.get("next"))
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = LoginUserForm()

    context["form"] = form

    return render(request=request, template_name="users/login.html", context=context)


@login_required
def custom_logout(request):
    """Функция для разлогирования"""

    logout(request)
    messages.info(request, f"Вы успешно вышли из своего аккаунта.")
    return redirect("from_start")


def subscribe(request):
    """Функция для подписки на новостные рассылки"""

    if request.method == "POST":
        name = request.POST.get("name", None)
        email = request.POST.get("email", None)

        if not name or not email:
            messages.error(
                request, "Необходимо ввести имя и email для подписки на новости"
            )
            return redirect("from_start")

        if get_user_model().objects.filter(email=email).first():
            messages.error(
                request,
                f"Найден зарегистрированный пользователь с таким же {email} email-адресом",
            )
            return redirect(request.META.get("HTTP_REFERER", "from_start"))

        subscribed_user = SubscribedUsers.objects.filter(email=email).first()
        if subscribed_user:
            messages.error(request, f"На этот email-адрес уже есть подписка: {email}")
            return redirect(request.META.get("HTTP_REFERER", "from_start"))

        try:
            validate_email(email)
        except ValidationError as err:
            messages.error(request, err.messages[0])
            return redirect("from_start")

        subscribe_model_instance = SubscribedUsers()
        subscribe_model_instance.name = name
        subscribe_model_instance.email = email
        subscribe_model_instance.save()
        messages.success(request, f"{email} email-адрес успешно подписан на новости.")
        return redirect(request.META.get("HTTP_REFERER", "from_start"))


@user_is_superuser
def newsletter(request):
    """Функция для формирования новостной рассылки"""

    context = {"title": "Новостная рассылка", "menu": ContextDataMenu}
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get("subject")
            receivers = form.cleaned_data.get("receivers").split(",")
            email_message = form.cleaned_data.get("message")

            mail = EmailMessage(
                subject,
                email_message,
                f"Trash_for_cash <{request.user.email}>",
                bcc=receivers,
            )
            mail.content_subtype = "html"

            if mail.send():
                messages.success(request, "Email отправлен")
            else:
                messages.error(request, "Возникла ошибка при отправке email")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

        return redirect("from_start")

    form = NewsletterForm()
    form.fields["receivers"].initial = ",".join(
        [active.email for active in SubscribedUsers.objects.all()]
    )
    context["form"] = form

    return render(
        request=request, template_name="contact/newsletter.html", context=context
    )


def contact(request):
    """Функция для отображения страницы: (Обратная связь)"""

    context = {"title": "Обратная связь", "menu": ContextDataMenu}

    if request.user.is_authenticated:
        data = {"name": request.user.username, "email": request.user.email}
        form = FeedbackFormForAuthenticatedUsers(data)
        if request.method == "POST":
            form = FeedbackFormForAuthenticatedUsers(request.POST)
            if form.is_valid():
                send_message(
                    form.cleaned_data["name"],
                    form.cleaned_data["email"],
                    form.cleaned_data["message"],
                )
                context["success_message"] = True
    else:
        if request.method == "POST":
            form = FeedbackForm(request.POST)
            if form.is_valid():
                send_message(
                    form.cleaned_data["name"],
                    form.cleaned_data["email"],
                    form.cleaned_data["message"],
                )
                context["success_message"] = True

        else:
            form = FeedbackForm()

    context["form"] = form

    return render(
        request,
        "contact/contact.html",
        context=context,
    )


def send_message(name, email, message):
    """Функция отправки сообщения для администрации сайта от кого бы то ни было"""

    text = get_template("contact/sending_message.html")
    html = get_template("contact/sending_message.html")
    context = {"name": name, "email": email, "message": message}
    subject = "Сообщение от кого-то"
    from_email = "from@example.com"
    text_content = text.render(context)
    html_content = html.render(context)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, ["lightcoach88@gmail.com"]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
