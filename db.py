import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv


def crear_base_datos():
  local_env_file = os.path.join(".envs", ".env.local")

  if os.path.isfile(local_env_file):
    load_dotenv(local_env_file)

  POSTGRES_DB = os.getenv("POSTGRES_DB")
  POSTGRES_USER = os.getenv("POSTGRES_USER")
  POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
  POSTGRES_HOST = os.getenv("POSTGRES_HOST")
  POSTGRES_PORT = os.getenv("POSTGRES_PORT")

  try:
    # Conectarse a la base de datos por defecto
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Verificar si la base de datos ya existe
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_DB,))
    exists = cur.fetchone()

    if exists:
      # Cerrar conexiones activas
      cur.execute(sql.SQL("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s AND pid <> pg_backend_pid()
      """), (POSTGRES_DB,))

      # Eliminar base de datos existente
      cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(POSTGRES_DB)))
      print(f"🗑️  Base de datos '{POSTGRES_DB}' eliminada.")

    # Crear la nueva base de datos
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(POSTGRES_DB)))
    print(f"✅ Base de datos '{POSTGRES_DB}' creada.")

    cur.close()
    conn.close()
  except Exception as e:
    print(f"❌ Error: {e}")


if __name__ == "__main__":
  crear_base_datos()
