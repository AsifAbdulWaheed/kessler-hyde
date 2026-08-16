"""
Production settings.
Used only when the website is deployed live — not used during
local development on your own computer.
"""
import os
from .base import *  # noqa

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("BREVO_SMTP_HOST", "smtp-relay.brevo.com")
EMAIL_PORT = int(os.environ.get("BREVO_SMTP_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("BREVO_SMTP_USER")
EMAIL_HOST_PASSWORD = os.environ.get("BREVO_SMTP_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@kesslerandhyde.com")