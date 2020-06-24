#!/bin/bash

redis-server &
celery -A immap beat -l info &
celery -A immap worker -l info
