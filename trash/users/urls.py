from django.urls import path

from .views import *

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", custom_login, name="login"),
    path("logout/", custom_logout, name="logout"),
    path("profile/<username>/", profile, name="profile"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("password_change/", password_change, name="password_change"),
    path("password_reset/", password_reset_request, name="password_reset"),
    path(
        "reset/<uidb64>/<token>/", password_reset_confirm, name="password_reset_confirm"
    ),
    path("subscribe/", subscribe, name="subscribe"),
    path("newsletter/", newsletter, name="newsletter"),
    path("contact/", contact, name="contact"),
]
