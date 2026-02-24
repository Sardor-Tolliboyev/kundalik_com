"""
'BilimNazoratchi' Loyihasi - Bildirishnomalar va Xabarlar yo'nalishlari (URLs).

Vazifasi:
1. Foydalanuvchi (ota-ona yoki o'qituvchi) o'ziga kelgan xabarlarni ko'rish manzillarini belgilash.
2. Xabarni batafsil o'qish va "O'qilgan" holatiga o'tkazish yo'llarini yaratish.
"""

from django.urls import path
from .views import xabarlar_ruyxati_view, xabarni_oqish_view

# Ilovaning noyob nomi (Namespace). 
# Bu shablonlarda yoki viewlarda 'xabarlar:ruyxat' ko'rinishida chaqirish imkonini beradi.
app_name = 'xabarlar'

urlpatterns = [
    
    # -------------------------------------------------------------------------
    # 1. BARCHA BILDIRISHNOMALAR RO'YXATI
    # -------------------------------------------------------------------------
    # Manzil: http://127.0.0.1:8000/xabarlar/ruyxat/
    # Vazifasi: Foydalanuvchiga tegishli barcha (yangi va eski) xabarlarni ko'rsatish.
    path(
        'ruyxat/', 
        xabarlar_ruyxati_view, 
        name='xabarlar_ruyxati'
    ),
    
    # -------------------------------------------------------------------------
    # 2. XABARNI BATAFSIL O'QISH
    # -------------------------------------------------------------------------
    # Manzil: http://127.0.0.1:8000/xabarlar/xabar/5/ (5 - bu xabar ID raqami)
    # Vazifasi: Tanlangan xabarni to'liq ko'rsatish va uni o'qilgan deb belgilash.
    path(
        'xabar/<int:xabar_id>/', 
        xabarni_oqish_view, 
        name='xabarni_oqish'
    ),
]