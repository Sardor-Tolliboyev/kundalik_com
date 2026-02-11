"""
'BilimNazoratchi' loyihasining asosiy URL yo'riqnomasi.
Ushbu fayl foydalanuvchi so'rovlarini tegishli ilovalarga (apps) yo'naltiradi.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# -------------------------------------------------------------------------
# ADMIN PANELNI O'ZBEKCHALASHTIRISH (BRANDING)
# -------------------------------------------------------------------------
admin.site.site_header = "BilimNazoratchi: Boshqaruv Paneli"
admin.site.site_title = "BilimNazoratchi"
admin.site.index_title = "Tizim ma'lumotlarini boshqarish bo'limi"

# -------------------------------------------------------------------------
# ASOSIY YO'NALISHLAR (URL PATTERNS)
# -------------------------------------------------------------------------
urlpatterns = [
    # 1. ADMIN PANEL YO'LI
    path('admin/', admin.site.urls),

    # 2. FOYDALANUVCHI HISOBLARI (Login, Logout, Parol o'zgartirish)
    # Manzil: http://127.0.0.1:8000/hisoblar/login/
    path('hisoblar/', include('django.contrib.auth.urls')),

    # 3. TA'LIM MANTIQLARI (Asosiy sahifa shu yerda)
    path('', include('apps.talim.urls')),

    # 4. TAHLIL VA STATISTIKA
    path('tahlil/', include('apps.tahlil.urls')),

    # 5. BILDIRISHNOMALAR (XABARLAR)
    path('xabarlar/', include('apps.xabarlar.urls')),
]

# -------------------------------------------------------------------------
# STATIK VA MEDIA FAYLLARNI QO'LLAB-QUVVATLASH
# -------------------------------------------------------------------------
if settings.DEBUG:
    # Statik fayllar (CSS, JS, Rasmlar)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Agar STATIC_ROOT bo'sh bo'lsa, STATICFILES_DIRS orqali ulaymiz
    if not settings.STATIC_ROOT:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

    # Foydalanuvchilar yuklagan fayllar (Media)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)