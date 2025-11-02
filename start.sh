#!/bin/bash
set -e

echo "Creating required directories..."
mkdir -p /app/logs /app/staticfiles /app/media

echo "Running database migrations..."
python manage.py migrate --noinput --settings=config.settings.production

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-file - --log-level info
