from django.contrib import admin
from trash_app.models import *

# Register your models here.


class TrashAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("name",)


class OrganizationsAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Об организации",
            {"fields": ("organization_name", "organization_description")},
        ),
        (
            "Контактная информация",
            {"fields": ("address", "telephone_number", "slug", "web_address")},
        ),
        ("Типы материалов для приёма в переработку", {"fields": ("material",)}),
        ("Дополнительная информация", {"fields": ("views", "active")}),
    ]
    list_display = ("id", "organization_name", "telephone_number")
    list_display_links = ("id", "organization_name")
    search_fields = ("organization_name", "material")
    list_filter = ("organization_name", "material")
    prepopulated_fields = {"slug": ("organization_name",)}


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published")
    list_display_links = ("id", "title")
    search_fields = ("title", "description", "release_date")
    list_editable = ("is_published",)
    list_filter = ("is_published", "release_date")
    prepopulated_fields = {"slug": ("title",)}


class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organizations_different_prices",
        "price_for_material",
    )
    list_display_links = ("id", "price_for_material")
    search_fields = ("organizations_different_prices",)
    list_filter = ("organizations_different_prices",)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "date_created", "date_updated")
    list_display_links = ("title",)
    list_filter = ("title",)
    prepopulated_fields = {"slug": ("title",)}


class AnswerAdmin(admin.ModelAdmin):
    list_display = ("answer", "author", "time_added", "reply")
    list_display_links = ("answer",)
    list_filter = ("author",)


admin.site.register(TrashMaterial, TrashAdmin)
admin.site.register(Organizations, OrganizationsAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
