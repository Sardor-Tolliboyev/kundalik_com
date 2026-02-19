from django.db import models
from django.conf import settings

# 1. SINF MODELI
class Sinf(models.Model):
    """Maktab sinflari (masalan: 4-A, 9-B) uchun model"""
    nomi = models.CharField("Sinf nomi", max_length=50, unique=True)

    class Meta:
        db_table = 'sinflar'
        verbose_name = "Sinf"
        verbose_name_plural = "Sinflar"

    def __str__(self):
        return self.nomi

# 2. FAN MODELI
class Fan(models.Model):
    """O'qitiladigan fanlar ro'yxati"""
    nomi = models.CharField("Fan nomi", max_length=100, unique=True)

    class Meta:
        db_table = 'fanlar'
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"

    def __str__(self):
        return self.nomi

# 3. MAVZU MODELI (Xatolik aynan shu yerda bo'lgan)
class Mavzu(models.Model):
    """Har bir dars uchun o'qituvchi tomonidan kiritiladigan mavzu"""
    sinf = models.ForeignKey(Sinf, on_delete=models.CASCADE, verbose_name="Sinf")
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, verbose_name="Fan")
    oqituvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 'oqituvchi'},
        verbose_name="O'qituvchi"
    )
    mavzu_nomi = models.CharField("Mavzu nomi", max_length=255)
    sana = models.DateField("Dars o'tilgan sana", auto_now_add=True)

    class Meta:
        db_table = 'dars_mavzulari'
        verbose_name = "Dars mavzusi"
        verbose_name_plural = "Dars mavzulari"
        unique_together = ('sinf', 'fan', 'sana') # Bir kunda bitta fandan bitta mavzu

    def __str__(self):
        return f"{self.sana} - {self.mavzu_nomi}"

# 4. BAHO MODELI
class Baho(models.Model):
    """O'quvchilarning mavzu bo'yicha olgan baholari"""
    oquvchi = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='baholari',
        limit_choices_to={'rol': 'oquvchi'},
        verbose_name="O'quvchi"
    )
    mavzu = models.ForeignKey(Mavzu, on_delete=models.CASCADE, related_name='baholar', verbose_name="Dars mavzusi")
    qiymati = models.PositiveSmallIntegerField("Baho") # 2, 3, 4, 5
    izoh = models.TextField("O'qituvchi izohi", blank=True, null=True)

    class Meta:
        db_table = 'baholar'
        verbose_name = "Baho"
        verbose_name_plural = "Baholar"
        unique_together = ('oquvchi', 'mavzu') # Bitta mavzuga bitta baho

    def __str__(self):
        return f"{self.oquvchi.username} - {self.qiymati}"