"""
Test settings for Django project.

Uses SQLite for faster test execution without requiring PostgreSQL/Supabase.
"""

from .base import *

# Use SQLite for tests to avoid dependency on Supabase
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for tests
]

# Test-specific settings
DEBUG = True  # Enable DEBUG for better error messages in tests
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['*']  # Allow all hosts for testing

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handler': 'null',
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
        },
        'apps': {
            'handlers': ['null'],
        },
    },
}