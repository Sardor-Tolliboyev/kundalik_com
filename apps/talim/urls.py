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
    
    path('', bosh_sahifa_view, name='bosh_sahifa'), # BU NOM NAVBARDA ISHLATILDI
    path('oqituvchi/dashboard/', oqituvchi_dashboard_view, name='oqituvchi_dashboard'),
    path('oquvchi/profil/', oquvchi_profil_view, name='oquvchi_profil'),
    path('farzandim/nazorat/', ota_ona_view, name='ota_ona_view'),
    path('oqituvchi/jurnal/<int:taqsimot_id>/', oqituvchi_jurnal_view, name='jurnal'),
]