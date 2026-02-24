"""
'BilimNazoratchi' Loyihasi - Analitika Boshqaruv Paneli.

Vazifasi:
1. O'quvchilarning o'rtacha ballarini monitoring qilish.
2. Bilim dinamikasi (Trend) va xavf guruhlarini vizual nazorat qilish.
3. Tahlil natijalarini qidirish va filtrlash.
"""

from django.contrib import admin
from .models import OquvchiTahlili

@admin.register(OquvchiTahlili)
class OquvchiTahliliAdmin(admin.ModelAdmin):
    """
    O'quvchilar bilim darajasi tahlilini ko'rsatuvchi professional panel.
    Eslatma: Ushbu bo'limdagi ma'lumotlar tizim algoritmi tomonidan 
    avtomatik hisoblanadi, shuning uchun tahrirlash cheklangan.
    """

    # --- 1. RO'YXAT SAHIFASI SOZLAMALARI ---
    
    # Jadval ustunlari: F.I.SH, Ball, Trend, Holat va Yangilanish vaqti
    list_display = (
        'oquvchi_fio', 
        'ortacha_ball', 
        'trend_vizual', 
        'holat_vizual', 
        'yangilangan_vaqt'
    )
    
    # O'ng tomondagi tezkor filtrlar
    list_filter = ('trend', 'xavf_ostida', 'yangilangan_vaqt')
    
    # Qidiruv maydonlari (O'quvchi ismi yoki logini bo'yicha)
    search_fields = (
        'oquvchi__username', 
        'oquvchi__first_name', 
        'oquvchi__last_name'
    )
    
    # Sahifadagi yozuvlar soni (Katta maktablar uchun optimallashgan)
    list_per_page = 25

    # --- 2. XAVFSIZLIK: FAQAT O'QISH REJIMI ---
    
    # Analitika natijalari tizim tomonidan shakllantiriladi, 
    # shuning uchun ularni admin panelda qo'lda o'zgartirib bo'lmaydi.
    readonly_fields = (
        'oquvchi', 
        'ortacha_ball', 
        'trend', 
        'xavf_ostida', 
        'yangilangan_vaqt'
    )

    # --- 3. MA'LUMOTLARNI OPTIMALLASHTIRISH (PERFORMANCE) ---
    
    def get_queryset(self, request):
        """Bazadan ma'lumot olishda o'quvchi modelini ham birga yuklaymiz"""
        return super().get_queryset(request).select_related('oquvchi')

    # --- 4. MAXSUS VIZUAL METODLAR ---

    @admin.display(description="O'quvchi (F.I.SH)")
    def oquvchi_fio(self, obj):
        """O'quvchining to'liq ismini chiroyli ko'rsatish"""
        return obj.oquvchi.get_full_name() or obj.oquvchi.username

    @admin.display(description="Bilim trendi")
    def trend_vizual(self, obj):
        """Trend holatini ikonka va rangli ko'rsatish"""
        if obj.trend == 'osish':
            return "📈 O'sish dinamikasi"
        elif obj.trend == 'pasayish':
            return "📉 Pasayish (Xavf)"
        return "➡ Barqaror holat"

    @admin.display(description="Tizim holati (Pulse)")
    def holat_vizual(self, obj):
        """Xavf darajasini rangli ko'rsatkich (Pulse) bilan ko'rsatish"""
        if obj.xavf_ostida:
            return "🔴 XAVF OSTIDA"
        return "🟢 YAXSHI"

    # Ro'yxatni o'rtacha ball bo'yicha eng pastidan boshlab tartiblash 
    # (Muammoli o'quvchilar birinchi ko'rinishi uchun)
    ordering = ('ortacha_ball',)