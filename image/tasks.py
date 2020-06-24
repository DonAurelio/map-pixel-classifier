from celery.decorators import task
from celery.utils.log import get_task_logger

import sqlite3
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

# from keras.models import load_model

import joblib
import time


logger = get_task_logger(__name__)


def update_sqlite_query(query_str,db_data):

    # Opening connecting
    connection = sqlite3.connect(db_data['database_name'])
    cursor = connection.cursor()

    # Performing query
    cursor.execute(query_str)
    connection.commit()

    # updated row count
    row_count = cursor.rowcount
   
    # Close connection
    connection.close()

    return row_count

@task(name="start_image_processing")
def start_image_processing(datacube_data,image_data,model_data,db_data):
    """sends an email when feedback form is filled successfully"""

    logger.info("Start Image Processing")

    # Change status of image to processing
    query_format = (
        'UPDATE image_simage SET '
        'status=\'%(status)s\' '
        'WHERE id=\'%(id)s\';'
    )

    WAITING = '0'
    PROCESSING = '1'
    PROCESSED =  '2'
    ERROR = '3'

    fields = {
        'status': PROCESSING,
        'id': image_data.get('id')
    }

    query_str = query_format % fields
    update_sqlite_query(query_str,db_data)
    
    # Loading datacube data
    product = datacube_data.get('product')
    platform = datacube_data.get('platform')
    latitude = datacube_data.get('latitude')
    longitude = datacube_data.get('longitude')
    time = datacube_data.get('time')

    # loading model data
    model_path = model_data.get('path')

    # Image data
    image_original_path = image_data.get('original_path')
    image_classified_path = image_data.get('classified_path')

    fields = {
        'status': PROCESSED,
        'id': image_data.get('id')
    }

    query_str = query_format % fields
    update_sqlite_query(query_str,db_data)

    logger.info("End Image Processing")


@task(name="start_image_processing_nb_1")
def start_image_processing_nb_1(image_data,model_data,db_data):
    """sends an email when feedback form is filled successfully"""

    logger.info("Start Image Processing - NB")
    
    # Loading image data
    image_id = image_data['id']
    image_file_path = image_data['file_url']
    image_classified_path = image_data['classified_path']

    data = xr.open_rasterio(image_file_path)
    inv = np.transpose(data.values)

    # loading model data
    model_path = model_data['path']
    model = joblib.load(model_path)

    # Perform predictions
    probabilities = []
    for i in range(0,inv.shape[0]):
        probabilities.append(model.predict(inv[i]))
    
    result = np.array(probabilities)
    # Axis = 2 es la dimesnion que contiene las probabilidad des 
    # de las predicciones realizadas sobre las bandas espectrales
    result = np.transpose(result)

    clases = { 
        'wofs': 0,
        'bosque': 1,
        'wofs_bosque': 2,
        'cloud': 3,
        'ninguno':4
    }

    for k,v in clases.items():
        result[result == k] = v

    result = result.astype(int)

    # Define las coordenadas de los puntos
    coords = {'x':data.x.values,'y':data.y.values}

    # Define el orden de las dimensiones
    dims = ('y','x')

    # Define los metadatos o atributos
    attrs = {
        'crs': data.crs,
        'transform': data.transform
    }

    data_array = xr.DataArray(data=result,coords=coords,dims=dims)

    west = str(min(data_array.x.values))
    east = str(max(data_array.x.values))
    south = str(min(data_array.y.values)) 
    north = str(max(data_array.y.values))

    plt.imsave(image_classified_path, data_array)

    query_format = (
        'UPDATE image_simage SET '
        'status=\'%(status)s\', '
        'west=\'%(west)s\', '
        'east=\'%(east)s\', '
        'south=\'%(south)s\', '
        'north=\'%(north)s\' '
        'WHERE id=\'%(id)s\';'
    )

    WAITING = '0'
    PROCESSING = '1'
    PROCESSED =  '2'
    ERROR = '3'

    fields = {
        'west': west,
        'east': east,
        'south': south,
        'north': north,
        'status': PROCESSED,
        'id': image_id
    }

    query_str = query_format % fields

    # Opening connecting
    connection = sqlite3.connect(db_data['database_name'])
    cursor = connection.cursor()

    # Performing query
    cursor.execute(query_str)
    connection.commit()

    # updated row count
    row_count = cursor.rowcount
   
    # Close connection
    connection.close()

    logger.info("End Image Processing - NB")

@task(name="start_image_processing_nb_2")
def start_image_processing_nb_2(image_data,model_data,db_data):
    """sends an email when feedback form is filled successfully"""

    logger.info("Start Image Processing - NB Gausiano")
    
    # Loading image data
    image_id = image_data['id']
    image_file_path = image_data['file_url']
    image_classified_path = image_data['classified_path']

    data = xr.open_rasterio(image_file_path)
    inv = np.transpose(data.values)

    # loading model data
    model_path = model_data['path']
    model = joblib.load(model_path)

    # Perform predictions
    probabilities = []
    for i in range(0,inv.shape[0]):
        probabilities.append(model.predict(inv[i]))
    
    result = np.array(probabilities)
    # Axis = 2 es la dimesnion que contiene las probabilidad des 
    # de las predicciones realizadas sobre las bandas espectrales
    result = np.transpose(result)

    clases = { 
        'wofs': 0,
        'bosque': 1,
        'wofs_bosque': 2,
        'cloud': 3,
        'ninguno':4
    }

    for k,v in clases.items():
        result[result == k] = v

    result = result.astype(int)

    # Define las coordenadas de los puntos
    coords = {'x':data.x.values,'y':data.y.values}

    # Define el orden de las dimensiones
    dims = ('y','x')

    # Define los metadatos o atributos
    attrs = {
        'crs': data.crs,
        'transform': data.transform
    }

    data_array = xr.DataArray(data=result,coords=coords,dims=dims)

    west = str(min(data_array.x.values))
    east = str(max(data_array.x.values))
    south = str(min(data_array.y.values)) 
    north = str(max(data_array.y.values))

    plt.imsave(image_classified_path, data_array)

    query_format = (
        'UPDATE image_simage SET '
        'status=\'%(status)s\', '
        'west=\'%(west)s\', '
        'east=\'%(east)s\', '
        'south=\'%(south)s\', '
        'north=\'%(north)s\' '
        'WHERE id=\'%(id)s\';'
    )

    WAITING = '0'
    PROCESSING = '1'
    PROCESSED =  '2'
    ERROR = '3'

    fields = {
        'west': west,
        'east': east,
        'south': south,
        'north': north,
        'status': PROCESSED,
        'id': image_id
    }

    query_str = query_format % fields

    # Opening connecting
    connection = sqlite3.connect(db_data['database_name'])
    cursor = connection.cursor()

    # Performing query
    cursor.execute(query_str)
    connection.commit()

    # updated row count
    row_count = cursor.rowcount
   
    # Close connection
    connection.close()

    logger.info("End Image Processing - NB Gausiano")
   