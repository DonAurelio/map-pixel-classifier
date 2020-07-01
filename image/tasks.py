from celery.decorators import task
from celery.utils.log import get_task_logger

import sqlite3
import numpy as np
import xarray as xr
import matplotlib as mpl
import matplotlib.pyplot as plt

# from keras.models import load_model

import joblib
import time

# Enable importing of utils.
import sys
sys.path.append('.')
print('PATH_SYS',sys.path)
# Load Data Cube Configuration
import datacube
import image.utils.data_cube_utilities.data_access_api as dc_api  
api = dc_api.DataAccessApi()
dc = api.dc

# Datacube analysis
from image.utils.data_cube_utilities.clean_mask import landsat_qa_clean_mask
from image.utils.data_cube_utilities.dc_mosaic import create_mosaic
from image.utils.data_cube_utilities.dc_mosaic import create_median_mosaic
from image.utils.data_cube_utilities.dc_rgb import rgb



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

def datacube_image_classifcation(datacube_data,model_data,image_data):

    # Loading datacube data
    product = datacube_data.get('product')
    platform = datacube_data.get('platform')
    latitude = datacube_data.get('latitude')
    longitude = datacube_data.get('longitude')
    time = datacube_data.get('time')


    landsat_dataset = dc.load(
        latitude=latitude,
        longitude=longitude,
        platform=platform,
        time=time,
        product=product,
        measurements=[
            'coastal_aerosol','red', 'green', 'blue', 
            'nir', 'swir1', 'swir2', 'pixel_qa','aerosol_qa',
            'radsat_qa'
        ]
    )

    # Masking Clouds
    cloud_mask = landsat_qa_clean_mask(landsat_dataset, platform=platform)
    cleaned_dataset = landsat_dataset.where(cloud_mask)

    # Create Mosaics
    least_recent_composite = create_mosaic(cleaned_dataset, cloud_mask.values, reverse_time=True)

    # Median composite
    #median_composite = create_median_mosaic(cleaned_dataset, cloud_mask)

    # Add indexes into the dataset
    least_recent_composite['rvi'] = (least_recent_composite.red)/(least_recent_composite.nir)
    least_recent_composite['ndvi'] = (least_recent_composite.nir-least_recent_composite.red )/(least_recent_composite.nir+least_recent_composite.red)
    least_recent_composite['evi'] = 2*((least_recent_composite.nir-least_recent_composite.red )/(least_recent_composite.nir+(6*least_recent_composite.red)-(7.5*least_recent_composite.blue)+1))
    least_recent_composite['evi2'] =  2*((least_recent_composite.nir-least_recent_composite.red )/(least_recent_composite.nir+(2.4*least_recent_composite.red)+1))
    least_recent_composite['lswi'] = (least_recent_composite.nir-least_recent_composite.swir1 )/(least_recent_composite.nir + least_recent_composite.swir1 )

    # Convert Dataset to Pandas Dataframe for prediction
    df = least_recent_composite.to_dataframe()

    # Remove NaN and Inf
    c = df[['coastal_aerosol','red', 'green', 'blue', 'nir', 'swir1', 'swir2', 'pixel_qa','aerosol_qa','radsat_qa', 'rvi', 'ndvi','evi','evi2','lswi']]
    c = c.dropna()
    c=c.replace([np.inf, -np.inf], -9999)

    # Load model and predict
    # loading model data
    model_path = model_data.get('path')
    model = joblib.load(model_path)

    prediccion = model.predict(c)
    print(prediccion)

    c['class'] = prediccion

    Final=c.to_xarray()
    
    cmap = mpl.colors.ListedColormap([
        'red','lime', 'yellowgreen', 'yellow', 'green',
        'orange', 'blue','white','silver','brown','peru'
    ])
    
    # Image data
    image_original_path = image_data.get('original_path')
    image_classified_path = image_data.get('classified_path')
    
    fig=Final["class"].transpose('latitude', 'longitude').plot(cmap=cmap, figsize = (16, 8))
    plt.savefig(image_classified_path, bbox_inches='tight')
    
    return Final

@task(name="start_image_processing")
def start_image_processing(datacube_data,image_data,model_data,db_data):
    """sends an email when feedback form is filled successfully"""

    logger.info("Start Image Processing")
    
    # Loading image data
    image_id = image_data['id']

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

    logger.info("datacube load and classification ... ")

    Final = datacube_image_classifcation(datacube_data,model_data,image_data)

    data_array = Final['class']

    west = str(min(data_array.longitude.values))
    east = str(max(data_array.longitude.values))
    south = str(min(data_array.latitude.values)) 
    north = str(max(data_array.latitude.values))

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
   
