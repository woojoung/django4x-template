"""
Django settings for project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import read_dotenv
# from hashlib import md5
# from library.enums import Environment

read_dotenv()

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'localhost')

DEFAULT_DB_NAME = os.environ.get('DEFAULT_DB_NAME')
DEFAULT_DB_USER = os.environ.get('DEFAULT_DB_USER')
DEFAULT_DB_PASSWORD = os.environ.get('DEFAULT_DB_PASSWORD')
DEFAULT_DB_HOST = os.environ.get('DEFAULT_DB_HOST')
DEFAULT_DB_PORT = os.environ.get('DEFAULT_DB_PORT')

API_DB_NAME = os.environ.get('API_DB_NAME')
API_DB_USER = os.environ.get('API_DB_USER')
API_DB_PASSWORD = os.environ.get('API_DB_PASSWORD')
API_DB_HOST = os.environ.get('API_DB_HOST')
API_DB_PORT = os.environ.get('API_DB_PORT')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = 0

AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_S3_BUCKET_PRIVATE = os.environ.get('AWS_S3_BUCKET_PRIVATE')
AWS_SES_SENDER = os.environ.get('AWS_SES_SENDER')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_APPLE_TEAM_ID = os.environ.get('AUTH_APPLE_TEAM_ID')
AUTH_APPLE_CLIENT_ID = os.environ.get('AUTH_APPLE_CLIENT_ID')
AUTH_APPLE_KEY_ID = os.environ.get('AUTH_APPLE_KEY_ID')
AUTH_APPLE_PRIVATE_KEY = Path(BASE_DIR / '_file' / 'README.md').read_text()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if ENVIRONMENT == 'localhost':
    DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'api',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

AUTH_USER_MODEL = "api.User"
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

DEFAULT_HTTP_TIMEOUT_SEC = 10
DEFAULT_PAGE_SIZE = 50
DEFAULT_TIMEZONE = 'Asia/Seoul'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
NEXT_PAGE_CHECK_BY_LIMIT_PLUS_ONE = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': DEFAULT_PAGE_SIZE,
    'DATETIME_FORMAT': DEFAULT_DATETIME_FORMAT,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ASGI_APPLICATION = 'project.asgi.application'
WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DEFAULT_DATABASE_ENGINE = 'mysql'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': DEFAULT_DB_NAME,
#         'USER': DEFAULT_DB_USER,
#         'PASSWORD': DEFAULT_DB_PASSWORD,
#         'HOST': DEFAULT_DB_HOST,
#         'PORT': DEFAULT_DB_PORT,
#     },
#     'api': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': API_DB_NAME,
#         'USER': API_DB_USER,
#         'PASSWORD': API_DB_PASSWORD,
#         'HOST': API_DB_HOST,
#         'PORT': API_DB_PORT,
#     },
# }

DATABASE_ROUTERS = ['library.database.DefaultDbRouter', 'library.database.ApiDbRouter']

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
# $ ./manage.py collectstatic
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'django_collect_static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = ['https://*.*.com']
if DEBUG:
    CSRF_TRUSTED_ORIGINS.append('https://*.ngrok.io')
