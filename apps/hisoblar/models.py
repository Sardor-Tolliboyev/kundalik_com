from django.contrib.auth.models import AbstractUser
from django.db import models

class Foydalanuvchi(AbstractUser):
    ROL_TANLOVI = (
        ('admin', 'Administrator'),
        ('oqituvchi', 'O‘qituvchi'),
        ('oquvchi', 'O‘quvchi'),
        ('ota_ona', 'Ota-ona'),
    )
    rol = models.CharField("Vazifasi", max_length=20, choices=ROL_TANLOVI, default='oquvchi')
    telefon = models.CharField("Telefon", max_length=15, blank=True, null=True)

    class Meta:
        db_table = 'foydalanuvchilar'
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"