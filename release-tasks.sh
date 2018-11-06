#!/usr/bin/env bash
python manage.py makemigrations authentication
python manage.py migrate authentication
python manage.py makemigrations
python manage.py migrate
