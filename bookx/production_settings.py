import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY", "")
