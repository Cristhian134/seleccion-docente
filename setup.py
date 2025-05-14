# setup.py
import os
import sys
import subprocess
from db import crear_base_datos
from django.contrib.auth import get_user_model


def run_setup():
  # Configuración del entorno de Django
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

  # 1. Crear o reiniciar la base de datos
  crear_base_datos()

  # 2. Ejecutar migraciones después de crear la base de datos
  try:
    subprocess.run(["python", "manage.py", "makemigrations"], check=True)
    subprocess.run(["python", "manage.py", "migrate"], check=True)
  except subprocess.CalledProcessError as e:
    print(f"❌ Error al ejecutar migraciones: {e}")
    return

  # 3. Llenar base de datos

  # 4. Creando superuser, puede acceder al sistema y a admin
  try:
    subprocess.run(["python", "manage.py", "create_superuser"], check=True)
  except Exception as e:
    print(f"❌ Error al crear superusuario: {e}")
    return

  # 5. Ejecutar Django (ej: runserver u otro comando)
  try:
    subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"], check=True)
  except subprocess.CalledProcessError as e:
    print(f"❌ Error al ejecutar Django: {e}")
    return


if __name__ == "__main__":
  run_setup()
