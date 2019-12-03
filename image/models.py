from django.db import models
from django.conf import settings

# Create your models here.

class SImage(models.Model):
    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    upload = models.FileField(upload_to='uploads/')
    north = models.CharField(max_length=200)
    south = models.CharField(max_length=200)
    east = models.CharField(max_length=200)
    west = models.CharField(max_length=200)
