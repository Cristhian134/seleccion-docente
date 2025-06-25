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
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": getenv("POSTGRES_DB"),
    "USER": getenv("POSTGRES_USER"),
    "PASSWORD": getenv("POSTGRES_PASSWORD"),
    "HOST": getenv("POSTGRES_HOST"),
    "PORT": getenv("POSTGRES_PORT"),
  }
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
