"""
Django settings for production environment.
Extends base.py with production-specific settings.
Used for Railway deployment and Supabase Cloud.
"""

import os
import dj_database_url
from .base import *  # noqa

# Production security settings
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable is not set')

# HTTPS and security headers
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# Database configuration for production (Supabase Cloud)
# Use DATABASE_URL from Railway environment
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
else:
    # Fallback to explicit Supabase settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('SUPABASE_DB_NAME'),
            'USER': os.environ.get('SUPABASE_DB_USER'),
            'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD'),
            'HOST': os.environ.get('SUPABASE_DB_HOST'),
            'PORT': os.environ.get('SUPABASE_DB_PORT', '5432'),
        }
    }

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Logging for production
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps.authentication']['level'] = 'INFO'
LOGGING['loggers']['apps.data_upload']['level'] = 'INFO'
LOGGING['loggers']['apps.analytics']['level'] = 'INFO'

# Static files configuration for Railway
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Whitelist middleware for production
MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Static files compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
