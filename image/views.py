from django.shortcuts import render, reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from image.models import SImage
from django.conf import settings

# Create your views here.

from django.views.generic.base import TemplateView

from image.tasks import start_image_processing

import os

class IndexView(TemplateView):

    def get(self,request,*args,**kwargs):
        template_name = 'image/index.html'
        return render(request,template_name)


class MapView(TemplateView):

    def get(self,request,*args,**kwargs):
        template_name = 'image/map.html'
        return render(request,template_name)

class UploadImage(CreateView):
    # Use simage_form.html as template implicity
    model = SImage
    fields = [
        'model','product','platform',
        'lat_min', 'lat_max','lon_min',
        'lon_max','date_min','date_max'
    ]

    def get_success_url(self):
        # return reverse('image:index', kwargs={'pk': self.object.pk})

        datacube_data = {
            'product': self.object.get_product_display(),
            'platform': self.object.get_platform_display(),
            'latitude': (self.object.lat_min,self.object.lat_max),
            'longitude': (self.object.lon_min,self.object.lon_max),
            'time': (self.object.date_min,self.object.date_max)
        }
        
        image_data = {
            'id': self.object.id,
            'original_path': os.path.join(settings.MEDIA_ROOT, str(self.object.id) + '.png' ),
            'classified_path': os.path.join(settings.MEDIA_ROOT, str(self.object.id) + '_labeled.png') 
        }

        db_data = {
            'database_name': settings.DATABASES['default']['NAME']
        }

        # "Random Forest"
        if self.object.model == SImage.Model_0:
            model_data = {
                'path': os.path.join(settings.MEDIA_ROOT,'RF.joblib')
            }
        # "Support Vector Machines"
        else:
            model_data = {
                'path': os.path.join(settings.MEDIA_ROOT,'SVM.joblib')
            }
        
        # Start image processing
        start_image_processing.delay(datacube_data,image_data,model_data,db_data)

        return reverse('image:list')

class ListImages(ListView):
    # Use simage_list.html as template implicity
    model = SImage


class DetailImage(DetailView):
    # Use simage_detail.html as template implicity
    model = SImage
