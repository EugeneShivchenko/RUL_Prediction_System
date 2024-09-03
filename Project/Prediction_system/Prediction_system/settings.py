"""
Настройки Django для проекта Prediction_system.

Создано 'django-admin startproject' с использованием Django 4.2.

Для получения дополнительной информации об этом файле см.
https://docs.djangoproject.com/en/4.2/topics/settings/

Полный список настроек и их значений см.
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from decouple import config
from pathlib import Path

# Создайте пути внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Настройки быстрого старта разработки — не подходят для производства
# См. https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: храните секретный ключ, используемый в производстве, в тайне!
SECRET_KEY = config('SECRET_KEY')

# ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: не запускайте с включенной отладкой в ​​рабочей среде!
DEBUG = config('DEBUG')

ALLOWED_HOSTS = []

# Определение приложения
INSTALLED_APPS = [
    'App',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Prediction_system.urls'

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

WSGI_APPLICATION = 'Prediction_system.wsgi.application'

# База данных
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = { 
    'default': { 
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': config('NAME'), 
        'USER': config('USER'), 
        'PASSWORD': config('PASSWORD'), 
        'HOST': config('HOST'), 
        'PORT': config('PORT'), 
        'OPTIONS': { 
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'" 
        } 
    } 
} 

# Проверка пароля
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

# Интернационализация
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, Изображения)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'

# Медиа-файлы (датасеты, модели МО, отчеты, масштабаторы)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип поля первичного ключа по умолчанию
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL-адреса перенаправления по умолчанию
LOGIN_REDIRECT_URL = 'account'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# Отображение веб-страниц в iframe
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Сессия должна истечь при закрытии браузера
SESSION_EXPIRE_AT_BROWSER_CLOSE = True