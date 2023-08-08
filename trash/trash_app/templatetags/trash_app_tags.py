from django import template
from django.shortcuts import redirect, render
from trash_app.models import *
from trash_app.forms import *

register = template.Library()

# @register.simple_tag(takes_context=True)
# def parametr_replace(context, **kwargs):
#     address = context['request'].GET.copy()
#     for key,value in kwargs.items():
#         address[key] = value
#     for key in [key for key, value in address.items() if not value]:
#         del address[key]
#     return address.urlencode()
