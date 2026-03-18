"""
'BilimNazoratchi' loyihasining markaziy URL (manzillar) yo'riqnomasi.

Vazifasi:
1. Foydalanuvchi so'rovlarini mantiqan tegishli ilovalarga (apps) yo'naltirish.
2. Admin panelini loyiha brendiga mos ravishda o'zbekchalashtirish.
3. Ishlab chiqish jarayonida dizayn (static) va media fayllarning ishlashini ta'minlash.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# -------------------------------------------------------------------------
# 1. ADMIN PANELNI PROFESSIONAL O'ZBEKCHALASHTIRISH (BRANDING)
# -------------------------------------------------------------------------
# Admin panelning tepa qismidagi asosiy sarlavha
admin.site.site_header = "BilimNazoratchi: Boshqaruv Markazi"

# Brauzer tabida (tepasida) ko'rinadigan nom
admin.site.site_title = "BilimNazoratchi"

# Admin panelning bosh sahifasidagi sarlavha matni
admin.site.index_title = "Tizim ma'lumotlarini boshqarish va monitoring bo'limi"


# -------------------------------------------------------------------------
# 2. ASOSIY YO'NALISHLAR (URL PATTERNS)
# -------------------------------------------------------------------------
urlpatterns = [
    # A) DJANGO ADMIN PANEL: Tizim administratorlari uchun maxsus yo'l
    path('admin/', admin.site.urls),

    # B) FOYDALANUVCHI HISOBLARI: Login, Logout, Profil va yo'naltirishlar
    # Manzillar 'apps/hisoblar/urls.py' faylidan olinadi
    path('hisoblar/', include('apps.hisoblar.urls')),

    # D) TA'LIM MANTIQLARI: Sinf, Fan, Jurnal, Baholash va Asosiy sahifa
    # Loyihaning markaziy qismi (URL bo'sh bo'lganda shu app ishlaydi)
    path('', include('apps.talim.urls')),

    # E) TAHLIL VA STATISTIKA: Matematik hisobotlar va o'quvchi grafiklari
    path('tahlil/', include('apps.tahlil.urls')),

    # F) BILD IRISHNOMALAR VA XABARLAR: Ota-onalar uchun ogohlantirish tizimi
    path('xabarlar/', include('apps.xabarlar.urls')),
]


# -------------------------------------------------------------------------
# 3. STATIK VA MEDIA FAYLLARNI QO'LLAB-QUVVATLASH
# -------------------------------------------------------------------------
# Loyihani ishlab chiqish (Development) bosqichida dizayn fayllari (CSS, JS) 
# va yuklangan rasmlar to'g'ri ko'rinishi uchun quyidagi professional blok shart:
if settings.DEBUG:
    # 1. Statik fayllar (Dizayn elementlari, JavaScript, Loyiha rasmlari)
    if settings.STATIC_URL and settings.STATICFILES_DIRS:
        urlpatterns += static(
            settings.STATIC_URL, 
            document_root=settings.STATICFILES_DIRS[0]
        )

    # 2. Media fayllar (Foydalanuvchilar tomonidan yuklanadigan hujjatlar yoki rasmlar)
    if settings.MEDIA_URL and settings.MEDIA_ROOT:
        urlpatterns += static(
            settings.MEDIA_URL, 
            document_root=settings.MEDIA_ROOT
        )

# Izoh: Loyiha serverga (Production) qo'yilganda, statik fayllar 
# Nginx yoki WhiteNoise kabi vositalar orqali xizmat ko'rsatiladi.
