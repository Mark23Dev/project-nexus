#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
  echo "Waiting for Postgres..."
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.2
  done
  echo "Postgres started"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

exec "$@"
