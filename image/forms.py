# -*- coding: utf-8 -*-

from django.forms import ModelForm
from image.models import SImage

# Create the form class.
class ArticleForm(ModelForm):
    class Meta:
        model = SImage
        exclude = ['status']