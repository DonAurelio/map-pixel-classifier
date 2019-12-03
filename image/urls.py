# -*- coding: utf-8 -*-

from django.urls import path
from image.views import IndexView
from image.views import UploadImage
from image.views import ListImages
from image.views import MapView
from image.views import DetailImage

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('upload/', UploadImage.as_view(), name='upload'),
    path('list/', ListImages.as_view(), name='list'),
    path('map/', MapView.as_view(), name='map'),
    path('<int:pk>/', DetailImage.as_view(), name='detail'),
]
