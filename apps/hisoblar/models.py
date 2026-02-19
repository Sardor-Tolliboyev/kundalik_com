from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

# -------------------------------------------------------------------------
# FOYDALANUVCHI MODELI: Tizimdagi barcha foydalanuvchilar uchun asosiy model
# -------------------------------------------------------------------------
class Foydalanuvchi(AbstractUser):
    """
    Django standart User modelidan meros olgan holda yaratilgan maxsus model.
    Vazifasi: O'qituvchi, O'quvchi va Ota-onalarni tizimda farqlash va 
    qo'shimcha ma'lumotlarni saqlash.
    """

    # 1. FOYDALANUVCHI NOMI (LOGIN)
    # Standart maydonni o'zbekcha yordamchi matnlar bilan qayta belgilaymiz
    username = models.CharField(
        "Foydalanuvchi nomi",
        max_length=150,
        unique=True,
        help_text="Majburiy. 150 tagacha belgi. Faqat harflar, raqamlar va @/./+/-/_ belgilari ruxsat etiladi.",
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': "Bunday foydalanuvchi nomi allaqachon mavjud.",
        },
    )

    # 2. TIZIMDAGI ROLLAR (VAZIFALAR)
    # Foydalanuvchi kimligini belgilovchi tanlovlar ro'yxati
    ROL_TANLOVI = (
        ('admin', 'Administrator'),
        ('oqituvchi', 'O‘qituvchi'),
        ('oquvchi', 'O‘quvchi'),
        ('ota_ona', 'Ota-ona'),
    )
    
    rol = models.CharField(
        "Tizimdagi vazifasi", 
        max_length=20, 
        choices=ROL_TANLOVI, 
        default='oquvchi'
    )

    # 3. QO'SHIMCHA SHAXSIY MA'LUMOTLAR
    telefon = models.CharField(
        "Telefon raqami", 
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Masalan: +998901234567"
    )

    # 4. OTA-ONA VA O'QUVCHI BOG'LIQLIGI
    # Agar foydalanuvchi ota-ona bo'lsa, unga o'quvchini biriktirish uchun
    farzandi = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'rol': 'oquvchi'}, # Faqat o'quvchilarni tanlash mumkin
        related_name='ota_onasi',
        verbose_name="Biriktirilgan o'quvchi",
        help_text="Faqat ota-ona foydalanuvchilari uchun to'ldiriladi."
    )

    # 5. MA'LUMOTLAR BAZASI SOZLAMALARI
    class Meta:
        db_table = 'foydalanuvchilar' # Bazadagi jadval nomi o'zbekcha bo'ladi
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        # Ism-familiya bo'yicha alifbo tartibida chiqarish
        ordering = ['first_name', 'last_name']

    # 6. OBYEKTNI MATN KO'RINISHIDA QAYTARISH
    def __str__(self):
        """Admin panel va qidiruvlarda foydalanuvchi qanday ko'rinishini belgilaydi"""
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.get_rol_display()})"
        return f"{self.username} ({self.get_rol_display()})"