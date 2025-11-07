import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# загружаем переменные из .env
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-yact%tw$ar(1i^(=k$_uu1w7up4dz&hvu!k1trrvp^=-rx7#*h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # наши приложения
    'accounts.apps.AccountsConfig',
    'core',           # абстрактные модели, утилиты
    'applications',   # модуль заявок

    # внешние библиотеки
    'rest_framework',                    # Django REST Framework
    'rest_framework_simplejwt.token_blacklist',  # (опционально) для чёрного списка JWT
    'corsheaders',                       # CORS-позволялка
    'django_filters',
    'drf_yasg',                          # Swagger/ReDoc-генерация
]

AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # обязательно — раньше, чем CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True

# Разрешаем запросы с Фронтенда (http://localhost:3000)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

# -----------------------------
from corsheaders.defaults import default_headers, default_methods
CORS_ALLOW_HEADERS = list(default_headers) + ["authorization"]
CORS_ALLOW_METHODS = list(default_methods)  # GET, POST, OPTIONS и т.д.
# Конфигурация DRF и JWT
# -----------------------------
# COOKIE-настройки для JWT


REST_FRAMEWORK = {
    # Стандартная аутентификация — JWT
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # По умолчанию все запросы требуют авторизации,
    # если не прописано AllowAny или другая пермишн-класс
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # (опционально) фильтрация и поиск
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    # Время жизни access-токена
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    # Время жизни refresh-токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # Включаем чёрный список при отзыве токенов
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'BLACKLIST_AFTER_ROTATION': True,
    'ROTATE_REFRESH_TOKENS': False,
}


ROOT_URLCONF = 'sarbaz_plus_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sarbaz_plus_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    # Оставляем Basic Auth (если нужно) и Session Auth
    'USE_SESSION_AUTH': True,

     # Описываем две схемы безопасности: Basic и Bearer
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic',
            'description': 'Используйте здесь ваши логин/пароль'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header: "Bearer <token>"',
        },
    },
}

# теперь можно читать os.getenv(...)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# JWT cookie settings
JWT_COOKIE_NAME = os.getenv('JWT_COOKIE_NAME', 'access_token')
JWT_REFRESH_COOKIE_NAME = os.getenv('JWT_REFRESH_COOKIE_NAME', 'refresh_token')
JWT_COOKIE_HTTPONLY = os.getenv('JWT_COOKIE_HTTPONLY') == 'True'
JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE') == 'True'
JWT_COOKIE_SAMESITE = os.getenv('JWT_COOKIE_SAMESITE', 'Lax')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'   # для теста чтобы код не уходил на реальную почту