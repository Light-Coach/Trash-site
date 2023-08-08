from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.


class CustomUser(AbstractUser):
    status_choose = (
        ("regular", "regular"),
        ("subscriber", "subscriber"),
        ("moderator", "moderator"),
    )

    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, choices=status_choose, default="regular")
    description = models.TextField("Описание", max_length=600, default="", blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username


class SubscribedUsers(models.Model):
    name = models.CharField("Имя", max_length=70)
    email = models.EmailField("Email", unique=True, max_length=100)
    created_date = models.DateTimeField("Время создания подписки", default=timezone.now)

    class Meta:
        verbose_name = "Пользователь, который подписан на рассылку"
        verbose_name_plural = "Пользователи, которые подписаны на рассылку"

    def __str__(self) -> str:
        return self.email
