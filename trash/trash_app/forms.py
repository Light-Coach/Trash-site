from typing import Any, Dict
from django import forms
from django.core.exceptions import ValidationError

from trash_app.models import *


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "content"]

    def __init__(self, *args, **kwargs):  # - переопределяем главный метод-конструктор;
        super().__init__(
            *args, **kwargs
        )  # - воздействуем на <QuestionForm> или на <ModelForm>? и переопределяем метод <__init__>;
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean_content(self):
        content = self.cleaned_data["content"]

        if len(content) > 2000:
            raise ValidationError("Длина превышает 2000 символов")
        return content


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)

        widgets = {"text": forms.Textarea({"class": "form-control"})}

    def clean_text(self):
        new_text = self.cleaned_data["text"]
        if len(new_text) > 2000:
            raise ValidationError("Длина превышает 2000 символов")
        return new_text
