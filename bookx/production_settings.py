import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/var/log/debug.log",
        }
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "DEBUG", "propagate": True}
    },
}

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
