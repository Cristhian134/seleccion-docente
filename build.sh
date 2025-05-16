#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r ./requirements/production.txt

echo "🔥 Borrando migraciones antiguas (excepto __init__.py)..."
find core_apps/common/migrations/ -type f ! -name '__init__.py' -name '*.py' -delete
find core_apps/common/migrations/ -type f -name '*.pyc' -delete

python manage.py collectstatic --no-input

python manage.py makemigrations
python manage.py migrate

python manage.py loaddata curso.json

python manage.py create_superuser