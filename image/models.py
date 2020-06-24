from django.db import models
from django.conf import settings

import os 

# Create your models here.

class SImage(models.Model):

    Model_0 = '0'
    Model_1 = '1'

    MODEL_SELECT = (
        (Model_0, "Neural Networks"),
        (Model_1, "Random Forest"),
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
        (IDEAM,'Geoscience Datacube'),
        (USGS,'United States Geological Survey USGS')
    )

    LS8_OLI_LARSRC = '0'

    PRODUCT = (
        (LS8_OLI_LARSRC,'LS8_OLI_LARSRC'),
    )

    LANDSAT_8 = '0'

    PLATFORM = (
        (LANDSAT_8,'LANDSAT_8'),
    )

    model = models.CharField(max_length=2,choices=MODEL_SELECT,default=Model_0)
    status = models.CharField(max_length=2,choices=PROCESSING_STATUS,default=WAITING)

    product = models.CharField(max_length=2,choices=PRODUCT,default=LS8_OLI_LARSRC)
    platform = models.CharField(max_length=2,choices=PLATFORM,default=LANDSAT_8)

    lat_min = models.CharField(
        'Latitude Min',
        help_text='Valid values 5.276905999999999 - 3.0384721000000003. Example: 3.6667',
        max_length=200
    )
    lat_max = models.CharField(
        'Latitude Max',
        help_text='Valid values 5.276905999999999 - 3.0384721000000003. Example: 3.9084',
        max_length=200
    )
    lon_min = models.CharField(
        'Longitude Min',
        help_text='Valid values -75.80698879999998,-74.491394. Example: -75.0216',
        max_length=200
    )
    lon_max = models.CharField(
        'Longitude Max',
        help_text='Valid values -75.80698879999998,-74.491394. Example: -74.8039',
        max_length=200)

    date_min = models.CharField('Date Min',max_length=20,help_text='Date format AAAA-MM-DD. Example: 2015-01-01')
    date_max = models.CharField('Date Max',max_length=20,help_text='Date format AAAA-MM-DD. Example: 2016-01-01')
