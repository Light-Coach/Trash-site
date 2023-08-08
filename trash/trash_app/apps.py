from django.apps import AppConfig


class TrashAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "trash_app"
    verbose_name = "Материалы для переработки"
