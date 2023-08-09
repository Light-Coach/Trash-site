from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from slugify import slugify

from map_app.views import get_client_ip
from map_app.models import ClientsIpAddresses
from trash_app.models import *
from trash_app.utils import *
from trash_app.forms import *

# Create your views here.


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def null_page(request):
    """Функция для отображения стартовой страницы"""

    return render(
        request,
        "trash_app/index.html",
        context={"title": "Начало", "menu": ContextDataMenu},
    )


def about_site(request):
    """Функция для отображения страницы сайта: (О сайте)"""

    return render(
        request,
        "trash_app/about_site.html",
        context={"title": "О сайте", "menu": ContextDataMenu},
    )


def organizations_showing(request):
    """Функция для показа организаций"""

    template = "trash_app/show_organizations.html"
    context = {
        "menu": ContextDataMenu,
        "title": "Организации",
    }

    organizations = Organizations.objects.filter(active=True).prefetch_related(
        "material"
    )
    paginator = Paginator(organizations, 2)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    context["pages"] = page
    context["organizations"] = organizations
    context["is_paginated"] = page.has_other_pages()

    if page.has_previous():
        context["previous_url"] = f"?page={page.previous_page_number()}"
    else:
        context["previous_url"] = ""

    if page.has_next():
        context["next_url"] = f"?page={page.next_page_number()}"
    else:
        context["next_url"] = ""

    return render(request, template, context=context)


def organization_showing(request, organization_slug):
    """Функция для показа организации"""

    template = "trash_app/show_organization.html"
    organization = Organizations.objects.get(slug=organization_slug)
    context = {
        "menu": ContextDataMenu,
        "title": organization.organization_name,
        "organization": organization,
    }

    ip = get_client_ip(request)

    if ClientsIpAddresses.objects.filter(ip=ip).exists():
        print("ip already present")
        organization.views.add(ClientsIpAddresses.objects.get(ip=ip))
    else:
        ClientsIpAddresses.objects.create(ip=ip)
        organization.views.add(ClientsIpAddresses.objects.get(ip=ip))

    return render(request, template, context=context)


def articles_showing(request):
    """Функция для показа статей"""

    template = "trash_app/show_articles.html"
    context = {
        "menu": ContextDataMenu,
        "title": "Статьи",
    }

    articles = Article.objects.filter(is_published=True)
    paginator = Paginator(articles, 2)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    context["pages"] = page
    context["articles"] = articles
    context["is_paginated"] = page.has_other_pages()

    if page.has_previous():
        context["previous_url"] = f"?page={page.previous_page_number()}"
    else:
        context["previous_url"] = ""

    if page.has_next():
        context["next_url"] = f"?page={page.next_page_number()}"
    else:
        context["next_url"] = ""

    return render(request, template, context=context)


def article_showing(request, article_slug):
    """Функция для показа статьи"""

    template = "trash_app/show_article.html"
    article = Article.objects.get(slug=article_slug)
    context = {"menu": ContextDataMenu, "title": article.title, "article": article}

    return render(request, template, context=context)


def questions_showing(request):
    """Функция для показа всех вопросов и создания нового вопроса"""

    template = "trash_app/show_questions.html"
    context = {"menu": ContextDataMenu, "title": "Вопросы"}

    success_message = False
    if request.method != "POST":
        form = QuestionForm()
    else:
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.author = request.user
            new_question.slug = slugify(new_question.title)
            new_question.save()
            success_message = True

    context["form"] = form
    context["success_message"] = success_message
    questions = Question.objects.all()
    paginator = Paginator(questions, 2)
    page_number = request.GET.get("page", 1)
    page = paginator.get_page(page_number)
    context["pages"] = page
    context["questions"] = questions
    context["is_paginated"] = page.has_other_pages()

    if page.has_previous():
        context["previous_url"] = f"?page={page.previous_page_number()}"
    else:
        context["previous_url"] = ""

    if page.has_next():
        context["next_url"] = f"?page={page.next_page_number()}"
    else:
        context["next_url"] = ""

    return render(request, template, context=context)


def question_with_answers(request, question_slug, pk):
    """Функция для отображения вопроса с ответами"""

    question = get_object_or_404(Question, slug=question_slug)
    context = {
        "menu": ContextDataMenu,
        "question": question,
        "title": Question.objects.values("title").get(slug=question_slug)["title"],
    }

    if question.likes.filter(id=request.user.id).exists():
        liked = True
    else:
        liked = False

    context["liked"] = liked

    answers = question.get_answers()
    paginator = Paginator(answers, 1)
    page_number = request.GET.get("pages_with_answers", 1)
    page_with_answers = paginator.get_page(page_number)
    context["pages_with_answers"] = page_with_answers

    context["is_paginated1"] = page_with_answers.has_other_pages()

    if page_with_answers.has_previous():
        context[
            "previous_url1"
        ] = f"?pages_with_answers={page_with_answers.previous_page_number()}"
    else:
        context["previous_url1"] = ""

    if page_with_answers.has_next():
        context[
            "next_url1"
        ] = f"?pages_with_answers={page_with_answers.next_page_number()}"
    else:
        context["next_url1"] = ""

    replies = Answer.objects.filter(answer__slug=question_slug).exclude(
        reply__isnull=True
    )
    paginator = Paginator(replies, 5)
    page_number = request.GET.get("pages_with_replies", 1)
    page_with_replies = paginator.get_page(page_number)
    context["pages_with_replies"] = page_with_replies

    context["is_paginated2"] = page_with_replies.has_other_pages()

    if page_with_replies.has_previous():
        context[
            "previous_url2"
        ] = f"?pages_with_replies={page_with_replies.previous_page_number()}"
    else:
        context["previous_url2"] = ""

    if page_with_replies.has_next():
        context[
            "next_url2"
        ] = f"?pages_with_replies={page_with_replies.next_page_number()}"
    else:
        context["next_url2"] = ""

    return render(request, "trash_app/show_question.html", context=context)


def edit_question(request, question_slug, pk):
    """Функция редактирования вопроса"""

    question = Question.objects.get(slug=question_slug)
    success_message_of_update = False

    form_for_editing = QuestionForm(request.POST, instance=question)
    if form_for_editing.is_valid():
        form_for_editing.save()
        success_message_of_update = True

    context = {
        "menu": ContextDataMenu,
        "title": "Редактирование вопроса",
        "question": question,
        "form": QuestionForm(instance=question),
        "success_message_of_update": success_message_of_update,
    }
    return render(request, "trash_app/edit_question.html", context=context)


def delete_question(request, question_slug, pk):
    """Функция для удаления вопроса"""

    question = Question.objects.get(slug=question_slug)
    question.delete()

    return redirect(reverse("show_questions"))


def like_question_view(request, pk):
    """Функция для добавления лайков к вопросам"""

    question = get_object_or_404(
        Question, id=request.POST.get("question_id")
    )  # - <button ... name="question_id">;

    if question.likes.filter(id=request.user.id).exists():
        question.likes.remove(request.user)
    else:
        question.likes.add(request.user)
    return redirect(request.GET.get("next"))


def add_answer(request, question_slug, pk):
    """Функция для создания ответа и комментария"""

    previous_page = (
        request.GET.get("next") if request.GET.get("next") is not None else ""
    )
    if request.method != "POST":
        form = AnswerForm()
    else:
        form = AnswerForm(request.POST)
        if form.is_valid():
            new_answer = form.save(commit=False)
            if request.POST.get("reply", None):
                new_answer.reply_id = int(request.POST.get("reply"))
            new_answer.author = request.user
            new_answer.answer_id = pk
            new_answer.save()
            return (
                redirect(previous_page)
                if previous_page != ""
                else redirect(
                    Question.objects.get(slug=question_slug).get_absolute_url()
                )
            )

    return render(
        request,
        "includes/add_answer.html",
        context={
            "form": form,
        },
    )


def edit_answer(request, question_slug, pk, id_of_answer):
    """Функция редактирования вопроса и комментария"""

    question = Question.objects.get(slug=question_slug)
    answer = Answer.objects.get(id=id_of_answer)
    success_message_of_update = False

    form_for_editing = AnswerForm(request.POST, instance=answer)
    if form_for_editing.is_valid():
        form_for_editing.save()
        success_message_of_update = True

    context = {
        "question": question,
        "menu": ContextDataMenu,
        "title": "Редактирование ответа",
        "answer": answer,
        "form": AnswerForm(instance=answer),
        "success_message_of_update": success_message_of_update,
    }
    return render(request, "trash_app/edit_answer.html", context=context)


def delete_answer(request, question_slug, pk, id_of_answer):
    """Функция удаления вопроса и комментария"""

    answer = Answer.objects.get(id=id_of_answer)
    answer.delete()

    return redirect(Question.get_absolute_url(Question.objects.get(slug=question_slug)))
