from django.shortcuts import render, reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from image.models import SImage


# Create your views here.

from django.views.generic.base import TemplateView

from image.tasks import start_image_processing


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
    fields = ['upload','model']

    def get_success_url(self):
        # return reverse('image:index', kwargs={'pk': self.object.pk})
        start_image_processing.delay(self.object)
        return reverse('image:index')

class ListImages(ListView):
	# Use simage_list.html as template implicity
    model = SImage
