"""
'BilimNazoratchi' loyihasining asosiy sozlamalari.
Ushbu fayl loyihaning barcha texnik qismlarini boshqaradi.
"""

import os
from pathlib import Path

# Loyihaning asosiy papkasi (bilim_nazoratchi/)
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================================
# 1. XAVFSIZLIK SOZLAMALARI
# =========================================================================

# Maxfiy kalit (Ishlab chiqish davrida shunday qoladi)
SECRET_KEY = 'django-insecure-bilim-nazoratchi-2026-pro-key'

# Debug rejimi (Xatoliklarni ko'rish uchun True bo'lishi shart)
DEBUG = True

# Ruxsat berilgan domenlar
ALLOWED_HOSTS = ['*']


# =========================================================================
# 2. ILOVALAR RO'YXATI (INSTALLED APPS)
# =========================================================================
INSTALLED_APPS = [
    # Admin panel interfeysini zamonaviy qiluvchi kutubxona (Admin'dan tepada turishi shart)
    'jazzmin',

    # Django standart ilovalari
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Biz yaratgan jamoaviy ilovalar (Apps papkasi ichidagilar)
    'apps.hisoblar',  # 1-talaba: Foydalanuvchilar va rollar
    'apps.talim',     # 2 va 4-talaba: Sinf, Fan, Mavzu, Baho
    'apps.tahlil',    # 5-talaba: Statistika va Analitika
    'apps.xabarlar',  # 4-talaba: Bildirishnomalar
]


# =========================================================================
# 3. ORALIK DASTURLAR (MIDDLEWARE)
# =========================================================================
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


# =========================================================================
# 4. SHABLONLAR (TEMPLATES) VA FRONTEND
# =========================================================================
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


# =========================================================================
# 5. MA'LUMOTLAR BAZASI (DATABASE - SQLite)
# =========================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================================================================
# 6. FOYDALANUVCHILARNI BOSHQARISH (AUTH)
# =========================================================================

# Biz yaratgan o'zbekcha Foydalanuvchi modeli
AUTH_USER_MODEL = 'hisoblar.Foydalanuvchi'

# Parol murakkabligini tekshirish sozlamalari
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================================================================
# 7. MAHALLIYLASHTIRISH (LOCALIZATION)
# =========================================================================

# Sayt tili: O'zbekcha
LANGUAGE_CODE = 'uz'

# Vaqt zonasi: O'zbekiston (Toshkent)
TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True


# =========================================================================
# 8. STATIK VA MEDIA FAYLLAR (CSS, JS, IMAGES)
# =========================================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================================================================
# 9. JAZZMIN (ADMIN PANEL) DIZAYN SOZLAMALARI
# =========================================================================
JAZZMIN_SETTINGS = {
    "site_title": "BilimNazoratchi",
    "site_header": "BilimNazoratchi",
    "site_brand": "BilimNazoratchi",
    "welcome_sign": "Maktab Monitoring Tizimiga Xush Kelibsiz!",
    "copyright": "BilimNazoratchi Jamoasi © 2026",
    "search_model": ["hisoblar.Foydalanuvchi"],
    "show_sidebar": True,
    "navigation_expanded": True,

    # Ilovalar va modellarga o'zbekcha ikonkalarni biriktiramiz (FontAwesome)
    "icons": {
        "hisoblar.Foydalanuvchi": "fas fa-user-graduate",
        "talim.Sinf": "fas fa-school",
        "talim.Fan": "fas fa-book",
        "talim.Baho": "fas fa-star",
        "talim.Mavzu": "fas fa-list-ul",
    },
    # Admin panelning tartibi
    "order_with_respect_to": ["hisoblar", "talim", "tahlil"],
}

# Admin panelning zamonaviy ko'k rangli temasi
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar": "navbar-primary",
    "sidebar": "sidebar-dark-primary",
}

LOGIN_URL = '/hisoblar/login/'
LOGIN_REDIRECT_URL = 'talim:bosh_sahifa' # Bu orqali foydalanuvchi roli bo'yicha dashboardga boradi
LOGOUT_REDIRECT_URL = '/hisoblar/login/'

# Standart ID maydoni turi
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'