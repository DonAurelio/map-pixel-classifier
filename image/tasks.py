from celery.decorators import task
from celery.utils.log import get_task_logger

import sqlite3

logger = get_task_logger(__name__)


@task(name="start_image_processing")
def start_image_processing(model_data,db_data):
    """sends an email when feedback form is filled successfully"""

    logger.info("Start Image Processing")
    
    model_id = model_data['id']
    model_file_url = model_data['file_url']
    model_name = model_data['id']


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
    	'status': PROCESSED,
    	'id': model_id

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

    logger.info("End Image Processing")
   