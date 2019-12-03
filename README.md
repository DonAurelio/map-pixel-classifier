# MAP PIXEL CLASSIFIER

This project deploys two machine learning models: **Multi Layer Perceptron** and **Multinomial Naive Bayes**for satelite image classification. It supports only geotif files generated by the [Colombian Geoescience Datacube](http://cdcol.ideam.gov.co/) for uploading and land cover classification. The aforementined model perform pixel classification over the uploaded images. Land cover is classified in one of 4 clases (water,forest,water_or_forest,unclasified). 

![alt text](https://raw.githubusercontent.com/DonAurelio/map-pixel-classifier/master/docs/classification.png)

## Deployment

Install redis

```sh
sudo apt install redis
```

Start redis server

```sh 
redis-server &
```

Check redis instalation

```sh 
redis-cli ping
```

Install requirements 

```sh 
pip3 install -r requirements.txt
```
Open a new términal and use the following command to enable a celery worker

```sh 
celery -A picha worker -l info
```

Open another terminal and use the following command to enable a the celery scheduler

```sh 
celery -A picha beat -l info
```

One more términal to run the django development server

```sh 
python3 manage.py runserver
```

## Contributors

* Aurelio Vivas, Arnold Lara, Felipe Cueto Daniel Martines

## References 

1. [Asynchronous Tasks With Django and Celery](https://realpython.com/asynchronous-tasks-with-django-and-celery/)
