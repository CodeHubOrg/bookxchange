from .settings import *  # NOQA

# DATABASES = {
#     "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "testdb",
#     }
# }


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
