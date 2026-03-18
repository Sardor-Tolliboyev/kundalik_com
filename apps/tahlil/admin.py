"""
'BilimNazoratchi' Loyihasi - Analitika boshqaruv paneli (Admin).

Vazifasi:
1) O'quvchilarning o'rtacha ballarini monitoring qilish.
2) Bilim dinamikasi (trend) va xavf guruhlarini nazorat qilish.
3) Tahlil natijalarini qidirish va filtrlash.
"""

from django.contrib import admin

from .models import OquvchiTahlili


@admin.register(OquvchiTahlili)
class OquvchiTahliliAdmin(admin.ModelAdmin):
    """
    O'quvchilar bilim darajasi tahlilini ko'rsatuvchi admin panel.

    # IZOH: Ushbu ma'lumotlar tizim algoritmi tomonidan avtomatik hisoblanadi,
    shuning uchun tahrirlash cheklangan.
    """

    list_display = (
        "oquvchi_fio",
        "ortacha_ball",
        "trend_vizual",
        "holat_vizual",
        "yangilangan_vaqt",
    )
    list_filter = ("trend", "xavf_ostida", "yangilangan_vaqt")
    search_fields = ("oquvchi__username", "oquvchi__first_name", "oquvchi__last_name")
    list_per_page = 25

    # # IZOH: Analitika natijalari tizim tomonidan shakllantiriladi,
    # shuning uchun ularni admin panelda qo'lda o'zgartirib bo'lmaydi.
    readonly_fields = ("oquvchi", "ortacha_ball", "trend", "xavf_ostida", "yangilangan_vaqt")

    def get_queryset(self, request):
        """
        Bazadan ma'lumot olishda o'quvchi modelini ham birga yuklaymiz.

        # IZOH: `select_related` N+1 muammosini kamaytiradi.
        """
        return super().get_queryset(request).select_related("oquvchi")

    @admin.display(description="O'quvchi (F.I.SH)")
    def oquvchi_fio(self, obyekt):
        return obyekt.oquvchi.get_full_name() or obyekt.oquvchi.username

    @admin.display(description="Bilim trendi")
    def trend_vizual(self, obyekt):
        if obyekt.trend == "osish":
            return "O'sish (ijobiy)"
        if obyekt.trend == "pasayish":
            return "Pasayish (xavf)"
        return "Barqaror"

    @admin.display(description="Tizim holati")
    def holat_vizual(self, obyekt):
        return "XAVF OSTIDA" if obyekt.xavf_ostida else "YAXSHI"

    # # IZOH: Ro'yxatni o'rtacha ball bo'yicha eng pastidan boshlab tartiblash
    # (muammoli o'quvchilar birinchi ko'rinishi uchun).
    ordering = ("ortacha_ball",)
