from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# -------------------------------------------------------------------------
# 1. SINF MODELI: Maktabdagi sinflarni saqlash uchun (masalan: 4-A, 9-B)
# -------------------------------------------------------------------------
class Sinf(models.Model):
    nomi = models.CharField("Sinf nomi", max_length=50, unique=True, help_text="Masalan: 9-A")

    # # IZOH: Sinf qaysi smenada o'qishini belgilash (jadval ko'rinishini ham shu boshqaradi).
    SMENA_TANLOVI = (
        ("1", "1-smena (08:00-13:00)"),
        ("2", "2-smena (13:00-17:55)"),
    )
    smena = models.CharField(
        "Smena",
        max_length=1,
        choices=SMENA_TANLOVI,
        default="1",
        help_text="Sinf qaysi smenada o'qishini tanlang.",
    )

    class Meta:
        db_table = "sinflar"
        verbose_name = "Sinf"
        verbose_name_plural = "Sinflar"
        ordering = ["nomi"]

    def __str__(self):
        return self.nomi


# -------------------------------------------------------------------------
# 2. FAN MODELI: O'qitiladigan fanlar ro'yxati (masalan: Matematika, Tarix)
# -------------------------------------------------------------------------
class Fan(models.Model):
    nomi = models.CharField("Fan nomi", max_length=100, unique=True)

    class Meta:
        db_table = "fanlar"
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"
        ordering = ["nomi"]

    def __str__(self):
        return self.nomi


# -------------------------------------------------------------------------
# 3. TAQSIMOT MODELI: O'qituvchini sinf, fan va vaqtga bog'lovchi dars jadvali
# -------------------------------------------------------------------------
class Taqsimot(models.Model):
    HAFTA_KUNLARI = (
        ("1", "Dushanba"),
        ("2", "Seshanba"),
        ("3", "Chorshanba"),
        ("4", "Payshanba"),
        ("5", "Juma"),
        ("6", "Shanba"),
    )

    oqituvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"rol": "oqituvchi"},
        related_name="biriktirilgan_darslari",
        verbose_name="Mas'ul o'qituvchi",
    )
    sinf = models.ForeignKey(
        Sinf,
        on_delete=models.CASCADE,
        related_name="dars_jadvali",
        verbose_name="Sinf",
    )
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, verbose_name="Fan")
    kun = models.CharField("Hafta kuni", max_length=1, choices=HAFTA_KUNLARI)
    soat = models.TimeField("Dars boshlanish vaqti")

    class Meta:
        db_table = "dars_taqsimotlari"
        verbose_name = "Dars taqsimoti"
        verbose_name_plural = "Darslar taqsimoti"
        unique_together = ("sinf", "kun", "soat")

    def __str__(self):
        return f"{self.sinf.nomi} | {self.fan.nomi} ({self.get_kun_display()})"


# -------------------------------------------------------------------------
# 4. DARSLAR (MAVZU) MODELI: O'qituvchi har bir dars kuni uchun kiritadigan mavzu
# -------------------------------------------------------------------------
class Mavzu(models.Model):
    taqsimot = models.ForeignKey(
        Taqsimot,
        on_delete=models.CASCADE,
        related_name="mavzulari",
        verbose_name="Dars jadvali bandi",
    )
    mavzu_nomi = models.CharField("Dars mavzusi", max_length=255)
    uy_vazifasi = models.TextField("Uyga vazifa", blank=True, null=True)
    sana = models.DateField("Dars o'tilgan sana")

    class Meta:
        db_table = "dars_mavzulari"
        verbose_name = "Dars mavzusi"
        verbose_name_plural = "Dars mavzulari"
        unique_together = ("taqsimot", "sana")

    def __str__(self):
        return f"{self.sana} | {self.mavzu_nomi}"


# -------------------------------------------------------------------------
# 5. BAHO MODELI: O'quvchining aniq bir dars mavzusi bo'yicha olgan natijasi
# -------------------------------------------------------------------------
class Baho(models.Model):
    oquvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="baholari",
        limit_choices_to={"rol": "oquvchi"},
        verbose_name="O'quvchi",
    )
    mavzu = models.ForeignKey(
        Mavzu,
        on_delete=models.CASCADE,
        related_name="baholar_ruyxati",
        verbose_name="Dars mavzusi",
    )
    qiymati = models.PositiveSmallIntegerField(
        "Baho",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 dan 5 gacha bo'lgan raqam",
    )
    izoh = models.CharField("O'qituvchi fikri", max_length=255, blank=True, null=True)

    class Meta:
        db_table = "baholar"
        verbose_name = "Baho"
        verbose_name_plural = "Baholar"
        unique_together = ("oquvchi", "mavzu")

    def __str__(self):
        return f"{self.oquvchi.username} -> {self.qiymati}"


# -------------------------------------------------------------------------
# 6. DAVOMAT MODELI: O'quvchining darsda ishtiroki tahlili
# -------------------------------------------------------------------------
class Davomat(models.Model):
    oquvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="davomati",
        limit_choices_to={"rol": "oquvchi"},
        verbose_name="O'quvchi",
    )
    mavzu = models.ForeignKey(
        Mavzu,
        on_delete=models.CASCADE,
        related_name="davomat_yozuvi",
        verbose_name="Dars mavzusi",
    )
    keldi = models.BooleanField("Ishtirok etdi", default=True)

    class Meta:
        db_table = "davomat"
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"
        unique_together = ("oquvchi", "mavzu")

    def __str__(self):
        holat = "Keldi" if self.keldi else "Kelmadi"
        return f"{self.oquvchi.username} - {self.mavzu.taqsimot.fan.nomi} ({holat})"
