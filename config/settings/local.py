"""
Django settings for local development environment.
Extends base.py with development-specific settings.
"""

import os
from .base import *  # noqa

# Development settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database Configuration - Inherit from base.py (supports both SQLite and PostgreSQL)
# If you want to force PostgreSQL, uncomment below:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('SUPABASE_DB_NAME', 'postgres'),
#         'USER': os.environ.get('SUPABASE_DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('SUPABASE_DB_HOST', '127.0.0.1'),
#         'PORT': os.environ.get('SUPABASE_DB_PORT', '54322'),
#     }
# }

# Session security settings (disabled for local development)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging level for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps.authentication']['level'] = 'DEBUG'
LOGGING['loggers']['apps.data_upload']['level'] = 'DEBUG'
LOGGING['loggers']['apps.analytics']['level'] = 'DEBUG'

# Create logs directory if it doesn't exist
import os
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
