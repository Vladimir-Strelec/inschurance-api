import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

# --- БЕЗОПАСНОСТЬ: делаем завязку на DEBUG ---
if DEBUG:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_PROXY_SSL_HEADER = None
else:
    ALLOWED_HOSTS = [
        "inschurance.online",
        "www.inschurance.online",
        "inschurance-api.onrender.com",
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://inschurance.online",
        "https://www.inschurance.online",
    ]
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Если за прокси (Render/NGINX) — пробрасываем схему
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

PREPEND_WWW = False


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'categories',
    'phonenumber_field',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'django.middleware.locale.LocaleMiddleware'
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     "default": dj_database_url.parse(
#         os.environ.get("DATABASE_URL", ""),
#         conn_max_age=600,
#         ssl_require=True,   # вот это критично на Render Postgres
#     ),
# }

if DATABASES.get("mysql", {}).get("ENGINE") == "django.db.backends.mysql":
    DATABASES["mysql"].setdefault("OPTIONS", {})

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "5/min",   # не больше 5 форм с одного IP в минуту
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "leads-cache",
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L10N = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"