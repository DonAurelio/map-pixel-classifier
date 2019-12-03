# -*- coding: utf-8 -*-

from django.urls import path
from image.views import IndexView
from image.views import UploadImage
from image.views import ListImages

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('upload/', UploadImage.as_view(), name='upload'),
    path('list/', ListImages.as_view(), name='list')
]