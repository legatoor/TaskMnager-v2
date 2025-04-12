"""
Django settings for taskmanager project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-changethisinproduction")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"


ALLOWED_HOSTS = ["*" if DEBUG else os.environ.get("ALLOWED_HOSTS", "localhost")]

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "members.apps.MembersConfig",
]

# Conditionally add REST framework if available
try:
    import rest_framework

    INSTALLED_APPS.append("rest_framework")
    INSTALLED_APPS.append("api.apps.ApiConfig")
except ImportError:
    pass

# Conditionally add channels if available
try:
    import channels

    INSTALLED_APPS.append("channels")

    # Channels configuration (only if channels is available)
    ASGI_APPLICATION = "taskmanager.asgi.application"

    # Channel Layers for WebSocket communication
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
    print("Django Channels is available and configured")
except ImportError:
    print("WARNING: Django Channels is not available")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "taskmanager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "members.context_processors.notifications",
                "members.context_processors.online_users",  # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = "taskmanager.wsgi.application"


# Database - PostgreSQL configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "taskmanager"),
        "USER": os.environ.get("DB_USER", "taskmanager_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "root"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "client_encoding": "UTF8",
            "options": f'-c search_path={os.environ.get("DB_SCHEMA", "taskmanager")}',
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
# Create STATICFILES_DIRS only if the directory exists
static_dir = BASE_DIR / "static"

# Create the static directory if it doesn't exist
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

STATICFILES_DIRS = [static_dir]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user-uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login and logout URLs
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"
