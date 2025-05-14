import dj_database_url
from os import getenv, path
from dotenv import load_dotenv
from .base import *  # noqa
from .base import BASE_DIR

local_env_file = path.join(BASE_DIR, ".envs", ".env.production")

if path.isfile(local_env_file):
  load_dotenv(local_env_file)

DJANGO_MIDDLEWARES = [
  "django.middleware.security.SecurityMiddleware",
  'whitenoise.middleware.WhiteNoiseMiddleware',
  "django.contrib.sessions.middleware.SessionMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.contrib.auth.middleware.AuthenticationMiddleware",
  "django.contrib.messages.middleware.MessageMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LOCAL_MIDDLEWARES = [
  'core_apps.middleware.Redirigir404Middleware',
  'core_apps.middleware.VerificarSesionMiddleware',
]

MIDDLEWARE = DJANGO_MIDDLEWARES + LOCAL_MIDDLEWARES


DATABASES = {
  'default': dj_database_url.config(
    # Replace this value with your local database's connection string.
    default='postgresql://selecciondocente_user:Bm8YdcvEQBy6FWD3Bs6WUyQLTYgL0FQZ@dpg-d0ihccje5dus739kljb0-a/selecciondocente',
    conn_max_age=600
  )
}


SECRET_KEY = getenv("SECRET_KEY")

# # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

ADMIN_URL = getenv("ADMIN_URL")

EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
DOMAIN = getenv("DOMAIN")

MAX_UPLOAD_SIZE = 1 * 1024 * 1024

CSRF_TRUSTED_ORIGINS = ["http://localhost:8080"]

LOCKOUT_DURATION = timedelta(minutes=1)

LOGIN_ATTEMPTS = 3

OTP_EXPIRATION = timedelta(minutes=1)
