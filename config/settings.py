"""
'BilimNazoratchi' loyihasining asosiy sozlamalari.
Ushbu fayl loyihaning barcha texnik qismlarini boshqaradi.
"""

import os
from pathlib import Path

# Loyihaning asosiy papkasi (bilim_nazoratchi/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Sozlamalar
# Maxfiy kalit
SECRET_KEY = 'django-insecure-bilim-nazoratchi-2026-pro-key'

# Debug rejimi 
DEBUG = True

# Ruxsat berilgan domenlar
ALLOWED_HOSTS = ['*']

# Ilovalar ro'yxati
INSTALLED_APPS = [
    # Django standart ilovalari
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Biz yaratgan jamoaviy ilovalar (Apps papkasi ichidagilar)
    'apps.hisoblar',  # Foydalanuvchilarni boshqarish: O'qituvchi, O'quvchi, Sinf rahbari
    'apps.talim',     # Ta'lim jarayonini boshqarish: Sinflar, Fanlar, Baholar, Mavzular
    'apps.tahlil',    # Tahlil va hisobotlar: O'quvchilarning baholari, o'qituvchilarning samaradorligi
    'apps.xabarlar',  # Xabarlar va bildirishnomalar: O'qituvchilar va o'quvchilar uchun xabarlar tizimi
]

# Oraliq qatlamlar (Middleware) ro'yxati
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'


# Shablonlar (Templates) sozlamalari
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # templates/ papkasini ulaymiz
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

WSGI_APPLICATION = 'config.wsgi.application'

# Ma'lumotlar bazasi sozlamalari (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Parol murakkabligini tekshirish sozlamalari
AUTH_USER_MODEL = 'hisoblar.Foydalanuvchi'

# Parol murakkabligini tekshirish sozlamalari
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Xalqaro sozlamalar
# Sayt tili: O'zbekcha
LANGUAGE_CODE = 'uz'

# Vaqt zonasi: O'zbekiston (Toshkent)
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True

# Statik va media fayllar sozlamalari
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/hisoblar/login/'
LOGIN_REDIRECT_URL = 'talim:bosh_sahifa' # Bu orqali foydalanuvchi roli bo'yicha dashboardga boradi
LOGOUT_REDIRECT_URL = '/hisoblar/login/'

# Standart ID maydoni turi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'