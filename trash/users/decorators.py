from django.shortcuts import redirect
from django.contrib import messages


def user_is_not_authenticated(function=None, redirect_url="from_start"):
    """Декоратор для определения состояния авторизации пользователя"""

    def decorator(view_function):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view_function(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def user_is_superuser(function=None, redirect_url="from_start"):
    """Декоратор для определения состояния суперпользователя"""

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_superuser:
                messages.error(
                    request, "Вы не уполномоченны совершать данные дейтсвия."
                )
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
