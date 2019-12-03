from django.db import models
from django.conf import settings

import os 

# Create your models here.

class SImage(models.Model):

    NN_1 = '1'
    NN_2 = '2'
    NB_1 = '3'
    NB_2 = '4'

    MODEL_SELECT = (
        (NN_1, "Red Neuronal 1"),
        (NN_2, "Red Neuronal 2"),
        (NB_1, "Naive Bayes 1"),
        (NB_2, "Naive Bayes 2")
    )

    WAITING = '0'
    PROCESSING = '1'
    PROCESSED =  '2'
    ERROR = '3'

    PROCESSING_STATUS = (
        (WAITING,'Waiting'),
        (PROCESSING,'Processing'),
        (PROCESSED,'Processed'),
        (ERROR,'Error')
    )

    IDEAM = '0'
    USGS = '1'

    SOURCE = (
        (IDEAM,'Colombia Geoscience Datacube IDEAM'),
        (USGS,'United States Geological Survey USGS')
    )


    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    upload = models.FileField(upload_to='uploads/')
    model = models.CharField(max_length=2,choices=MODEL_SELECT,default=NN_1)
    source = models.CharField(max_length=2,choices=SOURCE,default=USGS)
    status = models.CharField(max_length=2,choices=PROCESSING_STATUS,default=WAITING)
    north = models.CharField(max_length=200)
    south = models.CharField(max_length=200)
    east = models.CharField(max_length=200)
    west = models.CharField(max_length=200)

    def processed_path(self):
        return self.upload.name[:-4] + '_processed.png'

    def processed_url(self):
        return os.path.join(settings.MEDIA_URL,self.processed_path())