#!/bin/sh

set -e

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$1" = "test" ]; then
  pytest
else
  python manage.py flush --no-input
  python manage.py migrate
fi

exec "$@"