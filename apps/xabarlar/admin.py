"""
'BilimNazoratchi' Loyihasi - Bildirishnomalar Boshqaruvi (Admin).

Vazifasi:
1. Ota-onalarga yuborilgan barcha ogohlantirishlarni nazorat qilish.
2. Xabarlarni turi va o'qilganlik holati bo'yicha tahlil qilish.
3. Bir vaqtda bir nechta xabarni 'O'qilgan' deb belgilash (Action).
"""

from django.contrib import admin
from .models import Ogohlantirish

@admin.register(Ogohlantirish)
class OgohlantirishAdmin(admin.ModelAdmin):
    """
    Tizimdagi xabarlarni admin panelda professional boshqarish klassi.
    """

    # --- 1. RO'YXAT SAHIFASI SOZLAMALARI ---
    
    # Jadval ustunlarida nimalar ko'rinishi (F.I.SH, Turi, Sarlavha, Holat, Vaqt)
    list_display = (
        'kimga_fio', 
        'turi_vizual', 
        'sarlavha', 
        'oqilgan', 
        'yaratilgan_vaqt_format'
    )
    
    # O'ng tomondagi tezkor filtrlar (Xabar turi va o'qilganligi bo'yicha)
    list_filter = ('turi', 'oqilgan', 'yaratilgan_vaqt')
    
    # Qidiruv oynasi (Foydalanuvchi nomi, ismi yoki xabar matni orqali)
    search_fields = ('kimga__username', 'kimga__first_name', 'sarlavha', 'matn')
    
    # Ro'yxatning o'zida turib 'O'qilganmi?' belgisini o'zgartirish imkoniyati
    list_editable = ('oqilgan',)
    
    # Sahifadagi yozuvlar soni
    list_per_page = 20

    # --- 2. QUERY OPTIMIZATSIYASI (PERFORMANCE) ---
    
    def get_queryset(self, request):
        """Ma'lumotlarni bazadan olishda foydalanuvchini ham birga yuklaymiz (N+1 muammosi oldi olindi)"""
        return super().get_queryset(request).select_related('kimga')

    # --- 3. MAXSUS VIZUAL METODLAR (O'ZBEKCHA) ---

    @admin.display(description="Qabul qiluvchi (F.I.SH)")
    def kimga_fio(self, xabar):
        """Foydalanuvchining to'liq ismini ko'rsatadi"""
        return xabar.kimga.get_full_name() or xabar.kimga.username

    @admin.display(description="Xabar turi")
    def turi_vizual(self, xabar):
        """Xabar turini modeldagi emojilar bilan birga ko'rsatish"""
        return xabar.get_turi_display()

    @admin.display(description="Yuborilgan vaqt")
    def yaratilgan_vaqt_format(self, xabar):
        """Vaqtni o'zbekcha qulay formatda ko'rsatish"""
        return xabar.yaratilgan_vaqt.strftime("%d.%m.%Y | %H:%M")

    # --- 4. GURUXLI AMALLAR (ACTIONS) ---

    # Bir vaqtning o'zida ko'plab xabarlarni o'qilgan deb belgilash funksiyasi
    actions = ['oqilgan_deb_belgilash']

    @admin.action(description="Tanlangan xabarlarni 'O'qilgan' deb belgilash")
    def oqilgan_deb_belgilash(self, request, queryset):
        """Tanlangan barcha qatorlarni bazada bittada yangilaydi"""
        yangilangan = queryset.update(oqilgan=True)
        self.message_user(request, f"{yangilangan} ta xabar muvaffaqiyatli o'qilgan deb belgilandi.")

    # --- 5. TARTIBLASH ---
    # Yangi yuborilgan xabarlar har doim jadvalning eng tepasida chiqadi
    ordering = ('-yaratilgan_vaqt',)
