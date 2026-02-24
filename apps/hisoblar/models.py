from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator

# -------------------------------------------------------------------------
# FOYDALANUVCHI MODELI: Tizimdagi barcha shaxslarni boshqaruvchi asosiy sinf
# -------------------------------------------------------------------------
class Foydalanuvchi(AbstractUser):
    """
    Django'ning standart 'User' modelidan meros olgan holda yaratilgan professional model.
    Vazifasi: O'qituvchi, O'quvchi va Ota-onalarni tizimda farqlash va 
    ularning shaxsiy ma'lumotlarini (telefon, sinf, telegram) saqlash.
    """

    # --- 1. LOGIN (USERNAME) SOZLAMALARI ---
    # Standart maydonni o'zbekcha tushuntirish va validatorlar bilan boyitdik
    username = models.CharField(
        "Foydalanuvchi nomi (Login)",
        max_length=150, # Django standarti bo'yicha 150 belgi
        unique=True,
        help_text="Majburiy. 150 tagacha belgi. Faqat harflar, raqamlar va @/./+/-/_ belgilari ruxsat etiladi.",
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': "Bunday foydalanuvchi nomi tizimda allaqachon mavjud. Iltimos, boshqa nom tanlang.",
        },
    )

    # --- 2. SHAXSIY MA'LUMOTLAR (OVERRIDE) ---
    # Standart maydonlarni o'zbekcha nom (verbose_name) bilan qayta belgilaymiz
    first_name = models.CharField("Ismi", max_length=150, blank=True)
    last_name = models.CharField("Familiyasi", max_length=150, blank=True)
    email = models.EmailField("Elektron pochta manzili", blank=True)

    # --- 3. TIZIMDAGI ROLLARI (VAZIFALARI) ---
    # Foydalanuvchi kimligini aniqlash uchun variantlar
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
        default='oquvchi',
        help_text="Foydalanuvchining saytdagi vakolatlarini belgilaydi."
    )

    # --- 4. ALOQA MA'LUMOTLARI ---
    telefon = models.CharField(
        "Telefon raqami", 
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Namuna: +998901234567"
    )
    
    telegram_id = models.CharField(
        "Telegram ID raqami", 
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Telegram bot orqali bildirishnomalar yuborish uchun kerak."
    )

    # --- 5. O'QUV JARAYONI BILAN BOG'LIQLIK (POYDEVOR) ---
    
    # O'quvchini sinfga biriktirish (talim ilovasi bilan bog'lanadi)
    # Eslatma: 'talim.Sinf' ko'rinishida yozilishi aylana bog'liqlikni (circular import) oldini oladi
    sinf = models.ForeignKey(
        'talim.Sinf', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sinfdagi_oquvchilar',
        verbose_name="Sinfi",
        help_text="O'quvchi qaysi sinfda o'qishini belgilang."
    )

    # Ota-onani o'z farzandiga (o'quvchiga) bog'lash
    # 'self' - modelni o'z-o'ziga bog'lash (recursive relation)
    farzandi = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'rol': 'oquvchi'}, # Faqat o'quvchilarni tanlash imkoni
        related_name='ota_onasi',
        verbose_name="Biriktirilgan farzandi (O'quvchi)",
        help_text="Faqat ota-ona foydalanuvchisi uchun farzandini tanlang."
    )

    # --- 6. MODEL METADATA (SOZLAMALAR) ---
    class Meta:
        db_table = 'foydalanuvchilar' # Ma'lumotlar bazasidagi jadval nomi
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        # Yangi ro'yxatdan o'tganlar doim birinchi ko'rinadi
        ordering = ['-date_joined']

    # --- 7. MODEL METODLARI ---
    def __str__(self):
        """Foydalanuvchi obyektini matn ko'rinishida qaytarish qoidasi"""
        fio = self.get_full_name()
        if fio:
            return f"{fio} ({self.get_rol_display()})"
        return f"{self.username} ({self.get_rol_display()})"

    def save(self, *args, **kwargs):
        """Ma'lumotlarni saqlashdan oldin bajariladigan amallar"""
        # Masalan, loginlarni har doim kichik harfga o'tkazish (Professional yondashuv)
        self.username = self.username.lower()
        super().save(*args, **kwargs)