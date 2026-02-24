"""
'BilimNazoratchi' Loyihasi - Ta'lim jarayoni yo'nalishlari (URLs).

Vazifasi:
1. O'qituvchi, o'quvchi va ota-onalar uchun sahifa manzillarini belgilash.
2. Jurnal va baholash tizimiga kirish nuqtalarini yaratish.
"""

from django.urls import path
from .views import (
    bosh_sahifa_view, 
    oqituvchi_dashboard_view, 
    oqituvchi_jurnal_view,
    oquvchi_profil_view,
    ota_ona_view
)

# Shablonlarda (templates) ushbu yo'llarni chaqirish uchun namespace
app_name = 'talim'

urlpatterns = [
    
    # -------------------------------------------------------------------------
    # 1. ASOSIY YO'NALTIRUVCHI
    # -------------------------------------------------------------------------
    # Manzil: http://127.0.0.1:8000/
    path('', bosh_sahifa_view, name='bosh_sahifa'),

    # -------------------------------------------------------------------------
    # 2. O'QITUVCHI BO'LIMI
    # -------------------------------------------------------------------------
    # O'qituvchi ish stoli (Sinflar ro'yxati)
    path('oqituvchi/dashboard/', oqituvchi_dashboard_view, name='oqituvchi_dashboard'),

    # ELEKTRON JURNAL (Muvaffaqiyatli bog'liqlik uchun 'jurnal' nomi ishlatildi)
    # MUHIM: Bu nom templates/oqituvchi/dashboard.html dagi {% url 'talim:jurnal' %} ga mos keladi
    path('oqituvchi/jurnal/<int:taqsimot_id>/', oqituvchi_jurnal_view, name='jurnal'),

    # -------------------------------------------------------------------------
    # 3. O'QUVCHI BO'LIMI
    # -------------------------------------------------------------------------
    # O'quvchi shaxsiy profili
    path('oquvchi/profil/', oquvchi_profil_view, name='oquvchi_profil'),

    # -------------------------------------------------------------------------
    # 4. OTA-ONA BO'LIMI
    # -------------------------------------------------------------------------
    # Ota-ona uchun farzand nazorati
    path('farzandim/nazorat/', ota_ona_view, name='ota_ona_view'),
]