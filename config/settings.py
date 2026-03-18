"""
'BilimNazoratchi' loyihasining asosiy sozlamalari (settings.py).
Ushbu fayl loyihaning barcha texnik qismlarini, ma'lumotlar bazasini, 
xavfsizlik va xalqaro sozlamalarini markaziy tartibda boshqaradi.
"""

import os
from pathlib import Path

# 1. LOYIHA ASOSI (ROOT DIRECTORY)
# Loyihaning asosiy papkasi (bilim_nazoratchi/) yo'li
BASE_DIR = Path(__file__).resolve().parent.parent


# 2. XAVFSIZLIK SOZLAMALARI
# Maxfiy kalit (Ishlab chiqish vaqtida shunday qoladi, production uchun maxfiy saqlanishi shart)
SECRET_KEY = 'django-insecure-bilim-nazoratchi-2026-pro-key'

# Debug rejimi: True bo'lsa xatoliklarni ko'rsatadi. Productionda False bo'lishi shart.
DEBUG = True

# Ruxsat berilgan domenlar (Localhost uchun barcha manzillarga ruxsat berilgan)
ALLOWED_HOSTS = ['*','https://bilimnazoratchi.up.railway.app']


# 3. ILOVALAR RO'YXATI (INSTALLED APPS)
# Tizimga o'rnatilgan Django ilovalari va biz yaratgan lokal applar (modullar)
INSTALLED_APPS = [
    # Django standart (ichki) ilovalari
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Biz yaratgan jamoaviy ilovalar (Local Apps)
    'apps.hisoblar.apps.HisoblarConfig',  # Foydalanuvchilar: O'qituvchi, O'quvchi, Ota-ona tizimi
    'apps.talim.apps.TalimConfig',        # O'quv jarayoni: Sinf, Fan, Baho, Mavzu mantiqi
    'apps.tahlil.apps.TahlilConfig',      # Analitika: O'quvchilar ko'rsatkichlari va Pulse tizimi
    'apps.xabarlar.apps.XabarlarConfig',  # Bildirishnomalar: Ota-onalar uchun ogohlantirishlar
]


# 4. ORALIK QATLAM DASTURLARI (MIDDLEWARE)
# So'rovlarni (Request) qayta ishlash zanjiri (Tartib muhim!)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Statik fayllarni samarali yetkazib berish uchun (productionda ishlatiladi)
    'django.contrib.sessions.middleware.SessionMiddleware',      # Sessiyalarni boshqarish
    'django.middleware.locale.LocaleMiddleware',                # Admin va tizim matnlarini o'zbekchalashtirish
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                  # CSRF xavfsizligi
    'django.contrib.auth.middleware.AuthenticationMiddleware',      # Login tizimi
    'django.contrib.messages.middleware.MessageMiddleware',        # Xabarlar moduli
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Asosiy URL yo'riqnomasi fayli manzili
ROOT_URLCONF = 'config.urls'


# 5. SHABLONLAR (TEMPLATES) SOZLAMALARI
# HTML shablonlar (frontend) qayerda joylashganini belgilaydi
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # templates/ papkasini loyihaga ulaymiz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Shablonlarda 'request'dan foydalanish uchun
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Loyihani ishga tushiruvchi server konfiguratsiyasi (Web Server Gateway Interface)
WSGI_APPLICATION = 'config.wsgi.application'


# 6. MA'LUMOTLAR BAZASI (DATABASE - SQLite)
# Jamoaviy ishlash uchun SQLite fayl ko'rinishida tanlandi
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# 7. FOYDALANUVCHILARNI BOSHQARISH (AUTHENTICATION)
# Tizim biz yaratgan maxsus 'Foydalanuvchi' modelidan foydalanadi
AUTH_USER_MODEL = 'hisoblar.Foydalanuvchi'

# Parol murakkabligini tekshirish standartlari
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# 8. MAHALLIYLASHTIRISH (INTERNATIONALIZATION)
# Tizim tili va vaqtini O'zbekistonga moslaymiz
LANGUAGE_CODE = 'uz'

# # IZOH: Sayt faqat o'zbek tilida ishlaydi (inglizcha tanlov yo'q).
LANGUAGES = [
    ('uz', "O'zbek"),
]

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True # Ko'p tillilikni qo'llab-quvvatlash
USE_L10N = True # Raqam/Sana formatlarini mahalliylashtirish
USE_TZ = False   # MySQL va SQLite muammolarini oldini olish uchun False tavsiya etiladi

# IZOH: Loyiha admin tarjimalari uchun Django'ning o'z ichki (built-in) uz tarjimalari ishlatiladi.
# Kerakli joylar esa `templates/admin/*.html` override orqali bevosita o'zbekchalashtirilgan.


# 9. STATIK VA MEDIA FAYLLAR (CSS, JS, IMAGES)
# Saytning dizayn fayllari (Local static)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Server uchun statik fayllar yig'iladigan joy
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# WhiteNoise orqali fayllarni siqish va xotirada saqlash (Tezlik uchun)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Foydalanuvchilar yuklagan media fayllar (masalan, o'quvchi rasmi)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# 10. TIZIMGA KIRISH VA CHIQISH REDIREKTLARI (AUTH FLOW)
# Foydalanuvchi login qilishi kerak bo'lgan manzil
# settings.py faylining oxirida buni tasdiqlang:
# settings.py oxiri
LOGIN_URL = '/hisoblar/login/'

# Login qilganda 'hisoblar' appi ichidagi 'login_redirect' viewiga boradi
LOGIN_REDIRECT_URL = 'hisoblar:login_redirect'

# Logout qilganda yana login sahifasiga qaytadi
LOGOUT_REDIRECT_URL = 'hisoblar:login'

# 11. XAVFSIZLIK VA TIZIM SOZLAMALARI
# Standart ID maydoni turi (64 bitli butun son)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF xavfsizligi uchun ishonchli manzillar
CSRF_TRUSTED_ORIGINS = [ 'https://bilimnazoratchi.up.railway.app', 'http://127.0.0.1:8000', 'http://localhost:8000']
