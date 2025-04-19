#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create MongoDB indexes and prepare database
python manage.py makemigrations
python manage.py migrate --run-syncdb

# Collect static files
python manage.py collectstatic --no-input

# Create superuser (optional)
# if [ "$CREATE_SUPERUSER" = "yes" ]; then
#     python manage.py createsuperuser --noinput
# fi 