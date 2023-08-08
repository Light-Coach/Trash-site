from django.urls import path

from .views import *

urlpatterns = [
    path("", null_page, name="from_start"),
    path("about_site/", about_site, name="about_site"),
    path("show_organizations/", organizations_showing, name="show_organizations"),
    path(
        "show_organization/<slug:organization_slug>/",
        organization_showing,
        name="show_organization",
    ),
    path("show_articles/", articles_showing, name="show_articles"),
    path("show_article/<slug:article_slug>/", article_showing, name="show_article"),
    path("show_questions/", questions_showing, name="show_questions"),
    path(
        "edit_question/<slug:question_slug>/<int:pk>/",
        edit_question,
        name="edit_question",
    ),
    path(
        "delete_question/<slug:question_slug>/<int:pk>/",
        delete_question,
        name="delete_question",
    ),
    path(
        "question_detailed/<slug:question_slug>/<int:pk>/",
        question_with_answers,
        name="question_detailed",
    ),
    path(
        "question_detailed/<slug:question_slug>/<int:pk>/add_answer/",
        add_answer,
        name="add_answer",
    ),
    path(
        "question_detailed/<slug:question_slug>/<int:pk>/edit_answer/<int:id_of_answer>/",
        edit_answer,
        name="edit_answer",
    ),
    path(
        "question_detailed/<slug:question_slug>/<int:pk>/delete_answer/<int:id_of_answer>/",
        delete_answer,
        name="delete_answer",
    ),
    path('like/<int:pk>/', like_question_view, name='like_question'),
]
