import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "")

# ALLOWED_HOSTS = ["localhost", "138.68.176.181", "bookx.codehub.org.uk"]

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
