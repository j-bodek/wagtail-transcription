from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-k0&@(f0v_6%--nb#^-+igh!&a)r+)u#k2-o7!kv+xn*nv=6)0!"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "user",
        "PASSWORD": "1234",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

try:
    from .local import *
except ImportError:
    pass
