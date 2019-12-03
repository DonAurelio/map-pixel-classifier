from celery.decorators import task
from celery.utils.log import get_task_logger

from image.models import SImage

logger = get_task_logger(__name__)


@task(name="start_image_processing")
def start_image_processing(model):
    """sends an email when feedback form is filled successfully"""
    logger.info("Start Image Processing")
    model.status = SImage.PROCESSED
    model.save()

    