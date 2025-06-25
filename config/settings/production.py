from email.policy import default
import dj_database_url
from os import getenv, path
from dotenv import load_dotenv

from pathlib import Path

# Importar nuevo
from dotenv import load_dotenv
from os import getenv, path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Antiguo
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Nuevo
APPS_DIR = BASE_DIR / "core_apps"
local_env_file = path.join(BASE_DIR, ".envs", ".env.local")

if path.isfile(local_env_file):
  load_dotenv(local_env_file)

DJANGO_APPS = [
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  "django.contrib.sites",
  "django.contrib.humanize",
]

LOCAL_APPS = [
  "core_apps.autenticacion",
  "core_apps.common",
  "core_apps.protegido.home",
  "core_apps.protegido.crear_convocatoria",
  "core_apps.protegido.listar_docentes",
  "core_apps.protegido.ver_convocatorias",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
  {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [
      BASE_DIR / 'core_apps/autenticacion/templates',
      BASE_DIR / 'core_apps/common/templates',
      BASE_DIR / 'core_apps/protegido/home/templates',
      BASE_DIR / 'core_apps/protegido/crear_convocatoria/templates',
      BASE_DIR / 'core_apps/protegido/listar_docentes/templates',
      BASE_DIR / 'core_apps/protegido/ver_convocatorias/templates',
    ],
    "APP_DIRS": True,
    "OPTIONS": {
      "context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
      ],
    },
  },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database

DATABASES = {
  'default': dj_database_url.config(
    default=getenv("POSTGRES_URL"),
    conn_max_age=600
  )
}


PASSWORD_HASHERS = [
  "django.contrib.auth.hashers.Argon2PasswordHasher",
  "django.contrib.auth.hashers.PBKDF2PasswordHasher",
  "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
  "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
  "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
    "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
  },
  {
    "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
  },
  {
    "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
  },
  {
    "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
  },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "es-pe"

TIME_ZONE = 'America/Lima'  # Por ejemplo, para Perú

USE_I18N = True

USE_TZ = True

SITE_ID = 1

LOGIN_URL = 'login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = "/static/"
# STATIC_ROOT = str(BASE_DIR / "staticfiles")

STATIC_URL = '/static/'
STATIC_ROOT = path.join(BASE_DIR, 'staticfiles')

# Si deseas incluir archivos estáticos dentro de cada aplicación, asegúrate de tener:
STATICFILES_DIRS = [
  APPS_DIR / "autenticacion" / "static",
  APPS_DIR / "common" / "static",
  APPS_DIR / "protegido" / "home" / "static",
  APPS_DIR / "protegido" / "crear_convocatoria" / "static",
  APPS_DIR / "protegido" / "listar_docentes" / "static",
  APPS_DIR / "protegido" / "ver_convocatorias" / "static",
]

# Esta configuración es para las aplicaciones dentro del proyecto (como 'autenticacion')
STATICFILES_FINDERS = [
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

AUTH_USER_MODEL = "common.Usuario"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECRET_KEY = getenv("SECRET_KEY")

# # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "uni-seleccion-docente.onrender.com"]

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
