#!/usr/bin/env bash
python manage.py makemigrations authentication
python manage.py migrate authentication
python managy.py makemigrations article
python manage.py migrate article
python manage.py makemigrations profiles
python manage.py migrate profiles
python manage.py makemigrations
python manage.py migrate
