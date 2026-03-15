from django.urls import path
from .views import (
    landing_view, 
    bosh_sahifa_view, 
    oqituvchi_dashboard_view, 
    oqituvchi_jurnal_view, 
    oquvchi_profil_view, 
    ota_ona_view
)

app_name = 'talim'

urlpatterns = [
    # 1. Tizimga kirmaganlar ko'radigan landing (127.0.0.1:8000/)
    path('', landing_view, name='landing'), 

    # 2. Yo'naltiruvchi (Bu LOGIN_REDIRECT_URL uchun kerak)
    path('home/', bosh_sahifa_view, name='bosh_sahifa'),

    # 3. O'qituvchi yo'llari
    path('oqituvchi/dashboard/', oqituvchi_dashboard_view, name='oqituvchi_dashboard'),
    path('oqituvchi/jurnal/<int:taqsimot_id>/', oqituvchi_jurnal_view, name='jurnal'),
    
    # 4. O'quvchi va Ota-ona yo'llari
    path('oquvchi/profil/', oquvchi_profil_view, name='oquvchi_profil'),
    path('farzandim/nazorat/', ota_ona_view, name='ota_ona_view'),
]