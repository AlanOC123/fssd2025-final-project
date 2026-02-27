from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config


def csv_list(v: str):
    """
    Splits a comma separated list into individual string values and returns them as an array

    :param v: Commas separated list string
    :type v: str
    :return: String values of separated list
    :rtype: list[str]
    """
    return [s.strip() for s in v.split(",") if s.strip()]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment Settings ---
ENVIRONMENT = config("ENVIRONMENT", default="development")
IS_PROD = ENVIRONMENT == "production"
DEBUG = config("DEBUG", default=not IS_PROD, cast=bool)

# --- Environment Keys ---
SECRET_KEY = config("SECRET_KEY")
NINJA_API_KEY = config("NINJA_API_KEY")

if IS_PROD:
    BREVO_API_KEY = config("BREVO_API_KEY")
    CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET_KEY = config("CLOUDINARY_API_SECRET_KEY")

# --- Host Configuration ---
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=csv_list)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Application Definition ---

INSTALLED_APPS = [
    # Cloudinary Storage (Must be above static files)
    "cloudinary_storage",  # Cloudinary Toolkit
    # Core Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third Party Libraries
    "rest_framework",  # API Toolkit
    "rest_framework_simplejwt",  # JSON Web Token Support
    "rest_framework.authtoken",  # Token Authentication
    "corsheaders",  # Handles Cross-Origin Resource Sharing
    "dj_rest_auth",  # Auth Endpoints (Login, Logout, Password Reset)
    "dj_rest_auth.registration",  # Auth Endpoints (Registration)
    "allauth",  # Identity Infrastructure
    "allauth.account",  # Account Management
    "allauth.socialaccount",  # Social Authentication (For Google Sign In?)
    "anymail",  # HTTP Email Tool
    "cloudinary",  # Cloudinary Main App Support
    "django_rich",  # Debugging (Terminal)
    "django_extensions",  # Debugging (Werkzerg, Browser)
    # Apps
    "core",  # Apex Model
    "apps.analytics",  # Analytics App
    "apps.biology",  # Biology App
    "apps.energy",  # Energy App
    "apps.exercises",  # Exercises App
    "apps.notifications",  # Notifications App
    "apps.workouts",  # Workouts App
    "apps.users",  # Users App
    "apps.programs",  # Programs App
]

SITE_ID = 1  # Required for Site Identification and mapping by django.contrib.sites

MIDDLEWARE = [
    # CORS Requirement to come top level for preflight requests
    "corsheaders.middleware.CorsMiddleware",
    # Base Django Middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Required Middleware by allauth
    "allauth.account.middleware.AccountMiddleware",
    # Whitenoise required for Cloudinary
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "core.urls"

# Keeping for Django but templates not utilised
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# Web Server Settings
WSGI_APPLICATION = "core.wsgi.application"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {"datefmt": "[%X]"},
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "level": "INFO",
            "rich_tracebacks": True,
            "show_time": False,
            "show_path": False,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# --- Database Configuration ---

# Fail Early Here are Postgres is a Core Requirement
USE_POSTGRES = config("USE_POSTGRES", default=True, cast=bool)
DATABASE_URL = config("DATABASE_URL", cast=str)

# Use dj_database_url to parse the connection string.
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            str(DATABASE_URL), conn_max_age=600, ssl_require=IS_PROD
        )
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentication and Authorisation
# Configuring DRF to use JWT Cookies

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# --- CORS & CSRF (Frontend Integration)
CSRF_COOKIE_HTTP_ONLY = False  # Allows CSRF to be accessed by React if needed
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)

# Whitelisted Origins that can make a request
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="http://localhost:5173", cast=csv_list
)
CORS_TRUSTED_ORIGINS = config(
    "CORS_TRUSTED_ORIGINS", default="http://localhost:5173", cast=csv_list
)

# --- JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Short Lived Access Token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # Long Lived Refresh Token
    "ROTATE_REFRESH_TOKENS": False,  # New refresh token on every use
    "AUTH_HEADER_TYPES": ("Bearer",),  # JWT Header
    "BLACKLIST_AFTER_ROTATION": False,  # Not Necessary
    "REFRESH_TOKEN_LEEWAY": 20,  # 20 Second Leeway to Account for Transit Time
}

# --- dj-rest-auth Configuration
# Defines Security and Authentication Configuration for dj_rest_auth
REST_AUTH = {
    # Serializers
    "LOGIN_SERIALIZER": "dj_rest_auth.serializers.LoginSerializer",
    "TOKEN_SERIALIZER": "dj_rest_auth.serializers.TokenSerializer",
    "JWT_SERIALIZER": "dj_rest_auth.serializers.JWTSerializer",
    "JWT_SERIALIZER_WITH_EXPIRATION": "dj_rest_auth.serializers.JWTSerializerWithExpiration",
    "JWT_TOKEN_CLAIMS_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "USER_DETAILS_SERIALIZER": "apps.users.serializers.CustomUserSerializer",
    "PASSWORD_RESET_SERIALIZER": "dj_rest_auth.serializers.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "dj_rest_auth.serializers.PasswordResetConfirmSerializer",
    "PASSWORD_CHANGE_SERIALIZER": "dj_rest_auth.serializers.PasswordChangeSerializer",
    "REGISTER_SERIALIZER": "dj_rest_auth.registration.serializers.RegisterSerializer",
    # Permission Classes
    "REGISTER_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    # JWT Creation Settings
    "TOKEN_MODEL": "rest_framework.authtoken.models.Token",
    "TOKEN_CREATOR": "dj_rest_auth.utils.default_create_token",
    # Session Settings
    "PASSWORD_RESET_USE_SITES_DOMAIN": False,
    "OLD_PASSWORD_FIELD_ENABLED": False,
    "LOGOUT_ON_PASSWORD_CHANGE": False,
    "SESSION_LOGIN": False,
    "USE_JWT": True,
    # JWT Role Settings
    "JWT_AUTH_COOKIE": "auth_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_REFRESH_COOKIE_PATH": "/",
    "JWT_AUTH_SECURE": False,
    "JWT_AUTH_HTTPONLY": True,
    "JWT_AUTH_SAMESITE": "None",
    "JWT_AUTH_RETURN_EXPIRATION": True,
    "JWT_AUTH_COOKIE_USE_CSRF": False,
    "JWT_AUTH_COOKIE_ENFORCE_CSRF_ON_UNAUTHENTICATED": False,
}

# All Auth Configuration (Defaults for Now)
ACCOUNT_PREVENT_ENUMERATION = True
RATE_LIMITS = {
    "change_password": "5/m/user",
    "manage_email": "10/m/user",
    "reset_password": "20/min/ip,5/min/key",
    "login_failed": "10/m/ip,5/5m/key",
}

# Use Email instead of Username for authentication
ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD = [
    "address",
]

ACCOUNT_LOGIN_FIELDS = {"email"}

AUTH_USER_MODEL = "users.CustomUser"


# --- Production Only Settings ---

if IS_PROD:

    # --- Proxy and Host (Render Rewrites and Load Balancer)
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

    # Cookie Security
    REST_AUTH["JWT_AUTH_SECURE"] = True
    REST_AUTH["JWT_AUTH_SAMESITE"] = "Lax"

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Requirement for Render Rewrites & Safari Security
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    CORS_ALLOW_CREDENTIALS = True

    # Email (Current Strategy is Anymail + Brevo HTTP Approach)
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
    ANYMAIL = {"BREVO_API_KEY": BREVO_API_KEY}
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="dev@localhost")

# Password Validation
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

PASSWORD_RESET_LINK = config(
    "PASSWORD_RESET_LINK", default="http://localhost:5173/auth"
)

# --- Storage Configuration ---

# Static Files - Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media Files
if IS_PROD:
    # Cloudinary - Production
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUD_NAME"),
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET_KEY,
    }
else:
    # Django - Development
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary Configuration

# --- Internationalization & Static Files ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
