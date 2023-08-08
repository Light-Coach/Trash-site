from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from tinymce.models import HTMLField

from users.models import CustomUser

# Create your models here.


class TrashMaterial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название материала")
    image_of_material = models.ImageField(
        upload_to="images/%Y/%m/%d/", verbose_name="Изображения материала"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["name"]


class Organizations(models.Model):
    material = models.ManyToManyField(
        TrashMaterial,
        related_name="material_in_organization",
        verbose_name="Материалы",
    )
    organization_name = models.CharField(
        max_length=100, verbose_name="Название организации"
    )
    organization_description = HTMLField()
    slug = models.SlugField(
        max_length=100, unique=True, db_index=True, verbose_name="URL"
    )
    address = models.CharField(max_length=150, verbose_name="Адрес организации")
    telephone_number_validator = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Телефонный номер должен быть введён в формате: '+999999999'. Допускается до 15 цифр.",
    )
    telephone_number = models.CharField(
        validators=[telephone_number_validator],
        max_length=16,
        unique=True,
        verbose_name="Телефонный номер",
    )
    web_address = models.URLField("Адрес сайта", blank=True)
    views = models.ManyToManyField(
        "map_app.ClientsIpAddresses",
        related_name="question_views",
        blank=True,
        verbose_name="Ip-адреса просмотревших",
    )
    active = models.BooleanField(
        default=False, verbose_name="Статус организации (активна или нет)"
    )

    def __str__(self) -> str:
        return self.organization_name

    def get_absolute_url(self):
        return reverse("show_organization", kwargs={"organization_slug": self.slug})

    def total_views(self):
        return self.views.count()

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
        ordering = ["id"]


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    slug = models.SlugField(
        max_length=100, unique=True, db_index=True, verbose_name="URL"
    )
    photo_for_article = models.ImageField(
        upload_to="images/%Y/%m/%d/", verbose_name="Фото для статей"
    )
    description = HTMLField()
    release_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Публикация")
    material_name = models.ManyToManyField(
        TrashMaterial,
        related_name="article_of_material",
        blank=True,
        verbose_name="Материалы",
    )
    organization_name = models.ManyToManyField(
        Organizations,
        related_name="article_for_organization",
        blank=True,
        verbose_name="Организации",
    )

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("article_detailed", kwargs={"article_slug": self.slug})

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["release_date"]


class Price(models.Model):
    organizations_different_prices = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="organization_prices",
        verbose_name="Цены у разных организаций",
    )

    material_different_prices = models.ForeignKey(
        TrashMaterial,
        on_delete=models.CASCADE,
        related_name="material_prices",
        verbose_name="Цены на разные материалы",
    )

    price_for_material = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(0.0)],
        verbose_name="Цена за 1 кг",
    )

    def __str__(self) -> str:
        return str(self.organizations_different_prices)

    class Meta:
        verbose_name = "Цены за материал"
        verbose_name_plural = "Цены за материалы"
        ordering = ["organizations_different_prices"]


class Question(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="users_questions",
        verbose_name="Автор вопроса",
    )
    title = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Не более 50 символов",
        verbose_name="Заголовок",
    )
    content = models.TextField("Содержание вопроса")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    slug = models.SlugField(
        max_length=50, unique=True, db_index=True, verbose_name="URL"
    )
    likes = models.ManyToManyField(
        CustomUser, related_name="question_likes", blank=True
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["-date_created"]

    def __str__(self) -> str:
        return self.title

    def get_answers(self):
        return self.answers.filter(reply__isnull=True)

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse(
            "question_detailed", kwargs={"question_slug": self.slug, "pk": self.pk}
        )


class Answer(models.Model):
    answer = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers", verbose_name="Ответ"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="users_answers",
        verbose_name="Автор ответа",
    )
    text = models.TextField("Содержание ответа")
    time_added = models.DateTimeField(auto_now_add=True, verbose_name="Время ответа")
    time_changed = models.DateTimeField(
        auto_now=True, verbose_name="Время отредактированного ответа"
    )
    reply = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="answer_replies",
        blank=True,
        null=True,
    )
    likes = models.ManyToManyField(CustomUser, related_name="answer_likes", blank=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ["time_added"]

    def __str__(self) -> str:
        return "%s - %s" % (self.answer.title, self.author)
