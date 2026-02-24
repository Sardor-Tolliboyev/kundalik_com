"""
'BilimNazoratchi' Loyihasi - Analitika va Statistika yo'nalishlari (URLs).

Vazifasi:
1. O'quvchilarning umumiy ko'rsatkichlari sahifasiga yo'l ko'rsatish.
2. Matematik tahlil natijalarini vizual ko'rinishda chiqaruvchi sahifalarni bog'lash.
"""

from django.urls import path
from .views import statistika_markazi_view

# Ilovaning noyob nomi (Namespace). 
# Bu shablonlarda yoki viewlarda 'tahlil:statistika_markazi' ko'rinishida chaqirish uchun kerak.
app_name = 'tahlil'

urlpatterns = [
    
    # -------------------------------------------------------------------------
    # 1. UMUMIY STATISTIKA VA MONITORING SAHIFASI
    # -------------------------------------------------------------------------
    # Manzil: http://127.0.0.1:8000/tahlil/statistika/
    # Vazifasi: Maktab ma'muriyati yoki o'qituvchilar uchun barcha o'quvchilarning 
    # o'rtacha ballari, trendlari va xavf guruhlarini yagona jadvalda ko'rsatish.
    path(
        'statistika/', 
        statistika_markazi_view, 
        name='statistika_markazi'
    ),

    # Kelajakda quyidagi yo'llarni qo'shish uchun joy tayyor:
    # path('oquvchi/<int:pk>/', oquvchi_grafik_view, name='shaxsiy_grafik'),
    # path('sinf-hisoboti/', sinf_tahlili_view, name='sinf_hisoboti'),
]