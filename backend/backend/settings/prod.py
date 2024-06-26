from dotenv import find_dotenv, load_dotenv

from .base import *

load_dotenv(find_dotenv('.env.prod'))

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_SERVER'),
        'PORT': os.environ.get('POSTGRES_PORT'),
        'CONN_MAX_AGE': 0,
        'MAX_CONNECTIONS': 200,
    }
}


# Email server configuration

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Redis settings

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 1
