from django.db import models
from django.conf import settings

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

    PROCESSING = '1'
    PROCESSED =  '2'

    PROCESSING_STATUS = (
        (PROCESSING,'Processing'),
        (PROCESSED,'Processed')
    )

    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    upload = models.FileField(upload_to='uploads/')
    model = models.CharField(max_length=2,choices=MODEL_SELECT)
    status = models.CharField(max_length=2,choices=PROCESSING_STATUS)
    north = models.CharField(max_length=200)
    south = models.CharField(max_length=200)
    east = models.CharField(max_length=200)
    west = models.CharField(max_length=200)
