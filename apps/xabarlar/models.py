from django.conf import settings
from django.db import models


# -------------------------------------------------------------------------
# OGOHLANTIRISH MODELI: Tizimdagi bildirishnomalarni saqlash uchun
# -------------------------------------------------------------------------
class Ogohlantirish(models.Model):
    """
    Ushbu model tizim foydalanuvchilariga (asosan ota-onalarga) yuboriladigan
    xabarlar, baho/davomat haqidagi signallar va umumiy e'lonlarni saqlaydi.
    """

    # 1) XABAR TURLARI (CHOICES)
    # # IZOH: Choice matnlari faqat ko'rinish uchun. DBga ta'sir qilmaydi.
    XABAR_TURI = (
        ("baho", "Baho haqida ogohlantirish"),
        ("davomat", "Davomat (dars qoldirish)"),
        ("intizom", "Intizomiy ogohlantirish"),
        ("umumiy", "Umumiy e'lon yoki xabar"),
    )

    # 2) BOG'LIQLIK (FOREIGN KEY)
    kimga = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bildirishnomalari",
        verbose_name="Xabarni qabul qiluvchi",
        help_text="Xabar yuborilishi kerak bo'lgan foydalanuvchini tanlang.",
    )

    # 3) XABAR MAZMUNI
    sarlavha = models.CharField(
        "Xabar mavzusi",
        max_length=255,
        help_text="Xabarning qisqa sarlavhasi (masalan: Yangi baho qo'yildi).",
    )
    matn = models.TextField("Xabar to'liq matni", help_text="Xabarning batafsil mazmuni.")
    turi = models.CharField(
        "Xabar turi (toifasi)",
        max_length=20,
        choices=XABAR_TURI,
        default="umumiy",
    )

    # 4) HOLATLAR VA VAQT
    oqilgan = models.BooleanField(
        "O'qilganlik holati",
        default=False,
        help_text="Foydalanuvchi xabarni ochib ko'rgan bo'lsa belgilangan bo'ladi.",
    )
    yaratilgan_vaqt = models.DateTimeField("Yuborilgan sana va vaqt", auto_now_add=True)

    class Meta:
        db_table = "tizim_ogohlantirishlari"
        verbose_name = "Ogohlantirish"
        verbose_name_plural = "Ogohlantirishlar"
        ordering = ["-yaratilgan_vaqt"]

    def __str__(self):
        fio = self.kimga.get_full_name() or self.kimga.username
        return f"{fio} uchun: {self.sarlavha[:30]}..."

    def holat_belgisi(self):
        """
        Xabar o'qilgan yoki o'qilmaganligiga qarab holat matnini qaytaradi.
        """
        return "O'qildi" if self.oqilgan else "Yangi xabar"

