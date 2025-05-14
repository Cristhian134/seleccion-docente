# Ejecuta migraciones
python manage.py migrate --noinput

# Recolecta archivos estáticos
python manage.py collectstatic --noinput

# Inicia Gunicorn
gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --log-level info &

# Inicia nginx
nginx -g "daemon off;"