import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "")

ALLOWED_HOSTS = ["localhost", "138.68.176.181", "bookx.codehub.org.uk"]
