"""
Django settings for job_board project.
Production-grade configuration with all modern best practices.
"""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def config_bool(name, default=False):
    """Read common boolean-like env values used by local and hosted deploys."""
    value = config(name, default=default)
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
        return True
    if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
        return False
    raise ValueError(f"Invalid truth value for {name}: {value}")


def database_from_url(database_url):
    """Convert a Postgres DATABASE_URL into Django DATABASES settings."""
    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("DATABASE_URL must use postgres:// or postgresql://")

    database = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
    }
    options = {}
    for key, value in parse_qs(parsed.query).items():
        if key in {"sslmode", "connect_timeout"} and value:
            options[key] = value[-1]
    if options:
        database["OPTIONS"] = options
    return database


# SECURITY WARNING: keep the secret key used in production secret!
# config() reads from environment variables first, then .env — no default
# means it hard-crashes if missing.
SECRET_KEY = config("SECRET_KEY")  # required — no fallback
DEBUG = config_bool("DEBUG", default=False)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# HTTPS & Security Headers (for production)
SECURE_SSL_REDIRECT = config_bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = config_bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = config_bool("CSRF_COOKIE_SECURE", default=False)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": (
        "'self'",
        "'unsafe-inline'",
    ),  # Consider removing unsafe-inline in production
    "style-src": (
        "'self'",
        "'unsafe-inline'",
    ),  # Consider removing unsafe-inline in production
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'",),
}

# HSTS - Strict Transport Security
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
)
SECURE_HSTS_PRELOAD = config_bool("SECURE_HSTS_PRELOAD", default=False)

# Prevent clickjacking
X_FRAME_OPTIONS = "DENY"

# ============================================================================
# COOKIE SECURITY
# ============================================================================

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Session settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=1209600, cast=int)  # 2 weeks

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "django_htmx",
    "storages",
    # 'django_elasticsearch_dsl',  # Disabled - causing converter registration issues
    # Local apps
    "users.apps.UsersConfig",
    "jobs.apps.JobsConfig",
    "applications.apps.ApplicationsConfig",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "job_board.urls"

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
                "core.context_processors.theme_context",
            ],
        },
    },
]

WSGI_APPLICATION = "job_board.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Allow PostgreSQL for production
DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES["default"] = database_from_url(DATABASE_URL)
elif config_bool("USE_POSTGRES", default=False):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": config(
            "DB_CONN_MAX_AGE", default=600, cast=int
        ),  # Connection pooling
        "OPTIONS": {
            "connect_timeout": 10,
            "application_name": "job_board",
        },
    }
    db_sslmode = config("DB_SSLMODE", default="")
    if db_sslmode:
        DATABASES["default"]["OPTIONS"]["sslmode"] = db_sslmode

# Add connection pooling for better performance
if "OPTIONS" not in DATABASES["default"]:
    DATABASES["default"]["OPTIONS"] = {}

# Improve PostgreSQL performance
if DATABASES["default"].get("ENGINE") == "django.db.backends.postgresql":
    DATABASES["default"]["ATOMIC_REQUESTS"] = False  # Use explicit transactions
    DATABASES["default"]["AUTOCOMMIT"] = True  # Enable for high concurrency

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,  # Increased from default 8 for security
        },
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
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

USE_S3 = config_bool("USE_S3", default=False)
if USE_S3:
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default="")
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_QUERYSTRING_AUTH = config_bool("AWS_QUERYSTRING_AUTH", default=False)
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Auth redirect URLs
LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/users/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# ============================================================================
# REST FRAMEWORK & JWT CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.AcceptHeaderVersioning",
    "COERCE_DECIMAL_TO_STRING": False,
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME", default=60, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME", default=7, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": (
        "rest_framework_simplejwt.authentication.default_user_authentication_rule"
    ),
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_TYPE_CLAIM": "token_type",
}

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://localhost:8000",
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# ELASTICSEARCH CONFIGURATION
# ============================================================================

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": config("ELASTICSEARCH_HOST", default="localhost:9200"),
    },
}

# ============================================================================
# CACHE CONFIGURATION (REDIS WITH FALLBACK)
# ============================================================================

REDIS_URL = config("REDIS_URL", default="")
if REDIS_URL:
    # Production: Use Redis for distributed caching (Django 4.0+ built-in backend)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "TIMEOUT": 300,  # 5 minutes default
            "KEY_PREFIX": "jobboard",
            "VERSION": 1,
        }
    }
else:
    # Development/Test: Use local memory cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "job-board-cache",
            "OPTIONS": {
                "MAX_ENTRIES": 10000,
            },
            "TIMEOUT": 300,
        }
    }

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://redis:6379/1")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes

# Cache timeout constants
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 3600  # 1 hour
CACHE_TIMEOUT_LONG = 86400  # 24 hours

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config_bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@jobboard.com")

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "users": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "jobs": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# Trust X-Forwarded-Proto header from reverse proxy (e.g., Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ============================================================================
# PAGINATION & FILTERING
# ============================================================================

ITEMS_PER_PAGE = 20
MAX_PAGE_SIZE = 100

# ============================================================================
# FILE UPLOAD
# ============================================================================

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
ALLOWED_RESUME_EXTENSIONS = ["pdf", "doc", "docx"]
MAX_RESUME_SIZE = 5242880  # 5MB
