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

  # Eliminar migracion
  try:
    ruta_migracion = "core_apps/common/migrations/0001_initial.py"
    ruta_migracion_pyc = "core_apps/common/migrations/__pycache__/0001_initial.cpython-*.pyc"
    if os.path.exists(ruta_migracion):
      os.remove(ruta_migracion)
      print("✅ Migración 0001_initial.py eliminada")

    # También puedes eliminar el archivo .pyc si existe (opcional)
    import glob
    archivos_pyc = glob.glob(ruta_migracion_pyc)
    for archivo in archivos_pyc:
      os.remove(archivo)
      print(f"🧹 Archivo bytecode eliminado: {archivo}")
  except Exception as e:
    print(f"❌ Error al borrar la migracion: {e}")
    return

  # 2. Ejecutar migraciones después de crear la base de datos
  try:
    subprocess.run(["python", "manage.py", "makemigrations"], check=True)
    subprocess.run(["python", "manage.py", "migrate"], check=True)
  except subprocess.CalledProcessError as e:
    print(f"❌ Error al ejecutar migraciones: {e}")
    return

  # 3. Llenar base de datos
  print("🔃 Llenando las tablas de Usuarios y Convocatorias")
  try:
    subprocess.run(["python", "manage.py", "loaddata", "curso.json"], check=True)
    subprocess.run(["python", "manage.py", "populate_personas"], check=True)
    subprocess.run(["python", "manage.py", "populate_convocatorias"], check=True)
    print("✅ Llenado de Usuarios y Convocatorias")
  except Exception as e:
    print(f"❌ Error al llenar las tablas de Usuarios y Convocatorias: {e}")
    return

  # 4. Creando superuser, puede acceder al sistema y a admin
  try:
    subprocess.run(["python", "manage.py", "create_superuser"], check=True)
    subprocess.run(["python", "manage.py", "create_encargado_consejo"], check=True)
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
