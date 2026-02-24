from django.db import models
from django.conf import settings

# -------------------------------------------------------------------------
# OGOHLANTIRISH MODELI: Tizimdagi bildirishnomalarni saqlash uchun
# -------------------------------------------------------------------------
class Ogohlantirish(models.Model):
    """
    Ushbu model tizim foydalanuvchilariga (asosan ota-onalarga) yuboriladigan 
    xabarlar, baho haqidagi signallar va umumiy e'lonlarni saqlaydi.
    """

    # 1. XABAR TURLARI (CHOICES)
    # Emojilar admin panelda va saytda vizual qulaylik yaratadi
    XABAR_TURI = (
        ('baho', '📊 Baho haqida ogohlantirish'),
        ('davomat', '🕒 Davomat (dars qoldirish)'),
        ('intizom', '⚠️ Intizomiy ogohlantirish'),
        ('umumiy', '📢 Umumiy e’lon yoki xabar'),
    )

    # 2. BOG'LIQLIK (FOREIGN KEY)
    # Xabar kimga yuborilayotganini belgilaymiz.
    # settings.AUTH_USER_MODEL - loyihadagi maxsus Foydalanuvchi modeliga bog'lanadi.
    kimga = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bildirishnomalari',
        verbose_name="Xabarni qabul qiluvchi",
        help_text="Xabar yuborilishi kerak bo'lgan foydalanuvchini tanlang."
    )

    # 3. XABAR MAZMUNI
    sarlavha = models.CharField(
        "Xabar mavzusi", 
        max_length=255,
        help_text="Xabarning qisqa sarlavhasi (masalan: Yangi baho qo'yildi)."
    )
    matn = models.TextField(
        "Xabar to'liq matni",
        help_text="Xabarning batafsil mazmuni."
    )
    turi = models.CharField(
        "Xabar turi (toifasi)", 
        max_length=20, 
        choices=XABAR_TURI, 
        default='umumiy'
    )
    
    # 4. HOLATLAR VA VAQT
    oqilgan = models.BooleanField(
        "O‘qilganlik holati", 
        default=False,
        help_text="Foydalanuvchi xabarni ochib ko'rgan bo'lsa belgilangan bo'ladi."
    )
    yaratilgan_vaqt = models.DateTimeField(
        "Yuborilgan sana va vaqt", 
        auto_now_add=True # Avtomatik yuborilgan vaqtini yozadi
    )

    # --- MODEL METADATA (SOZLAMALARI) ---
    class Meta:
        db_table = 'tizim_ogohlantirishlari' # Bazadagi jadval nomi
        verbose_name = "Ogohlantirish"
        verbose_name_plural = "Ogohlantirishlar"
        # Yangi xabarlar har doim ro'yxatning eng tepasida chiqadi
        ordering = ['-yaratilgan_vaqt']

    # --- MODEL METODLARI ---
    def __str__(self):
        """Obyektni matn ko'rinishida qaytarish"""
        fio = self.kimga.get_full_name() or self.kimga.username
        return f"{fio} uchun: {self.sarlavha[:30]}..."

    def holat_belgisi(self):
        """Xabar o'qilgan yoki o'qilmaganligiga qarab belgi qaytaradi"""
        if self.oqilgan:
            return "✅ O'qildi"
        return "📩 Yangi xabar"