"""
Development settings.
This is used while you're building the project on your own computer.
"""
from .base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Emails print to the terminal instead of actually sending —
# safe for testing, no real customer email is ever contacted.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"