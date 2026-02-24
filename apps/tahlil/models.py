from django.db import models
from django.conf import settings

# -------------------------------------------------------------------------
# O'QUVCHI TAHLILI MODELI: Bilim ko'rsatkichlarini hisoblash va saqlash
# -------------------------------------------------------------------------
class OquvchiTahlili(models.Model):
    """
    Ushbu model har bir o'quvchining barcha fanlar bo'yicha baholarini 
    umumlashtirib, uning bilim darajasi va dinamikasini saqlaydi.
    Vazifasi: Tizim tezligini oshirish (har safar qayta hisoblamaslik uchun).
    """

    # 1. FOYDALANUVCHI BILAN BOG'LIQLIK
    # Har bir o'quvchi uchun faqat bitta tahlil yozuvi bo'ladi (OneToOneField)
    oquvchi = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tahlil_markazi',
        limit_choices_to={'rol': 'oquvchi'}, # Faqat o'quvchilar tahlil qilinadi
        verbose_name="O'quvchi"
    )

    # 2. BILIM KO'RSATKICHLARI
    # O'rtacha ball (Masalan: 4.5)
    ortacha_ball = models.DecimalField(
        "O'rtacha ball",
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        help_text="O'quvchining barcha fanlar bo'yicha jami o'rtacha natijasi."
    )

    # 3. BILIM DINAMIKASI (TREND)
    # Bilim darajasi o'syaptimi yoki pasayayotganini belgilash uchun variantlar
    TREND_TANLOVI = (
        ('osish', "📈 O‘sish dinamikasi (Ijobiy)"),
        ('pasayish', "📉 Pasayish dinamikasi (Xavf)"),
        ('barqaror', "➡ Barqaror holat"),
    )
    trend = models.CharField(
        "Bilim trendi", 
        max_length=20, 
        choices=TREND_TANLOVI, 
        default='barqaror',
        help_text="Oxirgi baholar tahlili asosida bilim o'zgarishi."
    )

    # 4. XAVF GURUHI MONITORINGI
    # O'quvchi orqada qolayotgan bo'lsa tizim avtomatik belgilaydi
    xavf_ostida = models.BooleanField(
        "Xavf ostidami?", 
        default=False,
        help_text="Agar o'rtacha ball 3.5 dan past bo'lsa, ota-onaga ogohlantirish yuboriladi."
    )

    # 5. VAQT KO'RSATKICHLARI
    # Tahlil oxirgi marta qachon yangilangani (avtomatik yangilanadi)
    yangilangan_vaqt = models.DateTimeField(
        "Oxirgi tahlil vaqti", 
        auto_now=True
    )

    # --- MODEL SOZLAMALARI ---
    class Meta:
        db_table = 'oquvchi_tahlillari' # Ma'lumotlar bazasidagi jadval nomi
        verbose_name = "O'quvchi tahlili"
        verbose_name_plural = "O'quvchilar tahlillari"
        # Natijalar o'rtacha ball bo'yicha tartiblanadi (eng pastlari tepada chiqishi uchun)
        ordering = ['ortacha_ball']

    # --- METODLAR ---
    def __str__(self):
        """O'quvchi ismi va natijasini matn ko'rinishida qaytarish"""
        fio = self.oquvchi.get_full_name() or self.oquvchi.username
        return f"{fio} - Natija: {self.ortacha_ball}"

    def holat_rangini_olish(self):
        """Frontend (CSS) uchun dinamik rang qiymatini qaytaradi"""
        if self.xavf_ostida:
            return "danger" # Qizil
        if self.ortacha_ball >= 4.5:
            return "success" # Yashil
        if self.ortacha_ball >= 3.5:
            return "warning" # Sariq
        return "secondary" # Kulrang