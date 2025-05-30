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
python manage.py populate_personas || echo "Error al generar las personas"
python manage.py populate_convocatorias || echo "Error al generar las convocatorias"

python manage.py create_encargado_consejo || echo "Ya hay un encargado consejo"
python manage.py create_superuser || echo "Ya hay un superuser"
