from django.urls import path
from .views import (
    landing_view,
    bosh_sahifa_view, 
    haftalik_dars_jadvali_view,
    oqituvchi_dashboard_view, 
    oqituvchi_jurnal_view,
    oquvchi_profil_view,
    ota_ona_view
)

app_name = 'talim'

urlpatterns = [
    # 1. ASOSIY LANDING (127.0.0.1:8000/) 
    # Saytga birinchi kirgan odam buni ko'radi. Login shart emas.
    path('', landing_view, name='landing'),

    # 2. YO'NALTIRUVCHI (127.0.0.1:8000/home/)
    # Faqat login qilganlar uchun. Bu dashboard-larni tanlab beradi.
    path('home/', bosh_sahifa_view, name='bosh_sahifa'), 

    # 2.5 HAFTALIK DARS JADVALI (BARCHA ROLLAR UCHUN)
    path('dars-jadvali/', haftalik_dars_jadvali_view, name='haftalik_dars_jadvali'),

    # 3. O'QITUVCHI BO'LIMI
    path('oqituvchi/dashboard/', oqituvchi_dashboard_view, name='oqituvchi_dashboard'),
    path('oqituvchi/jurnal/<int:taqsimot_id>/', oqituvchi_jurnal_view, name='jurnal'),
    
    # 4. O'QUVCHI VA OTA-ONA BO'LIMI
    path('oquvchi/profil/', oquvchi_profil_view, name='oquvchi_profil'),
    path('farzandim/nazorat/', ota_ona_view, name='ota_ona_view'),
]
