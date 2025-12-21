from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-i1d^n(q8gkw*574@d*e0hz5b9y!ym-zxq8vzgh1#bv4*uv1skh")

# SECURITY WARNING: don't run with debug turned on in production!
# os.getenv reads as string to need to convert to bool here
DEBUG = False if os.getenv("DEBUG", "").lower() == "false" else True


ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # DRF
    "rest_framework.authtoken",
    "rest_framework",
    # Djoser
    "djoser",
    # Apps
    "users.apps.UsersConfig",
    "recipes.apps.RecipesConfig",
    "shortlinks.apps.ShortlinksConfig",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram_backend.wsgi.application"

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation."
                 "UserAttributeSimilarityValidator"),
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS":
    ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE":
    10,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user": "api.serializers.UserSerializer",
        "user_create": "api.serializers.UserShortSerializer",
        "current_user": "api.serializers.UserSerializer",
        "token_create": "api.serializers.TokenCreateSerializer",
    },
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
        "user_list": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    },
}
