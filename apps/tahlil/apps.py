from django.apps import AppConfig

class TahlilConfig(AppConfig):
    """
    'Tahlil' ilovasi sozlamalari. 
    Ushbu bo'lim o'quvchilar ko'rsatkichlarini matematik monitoring qilish uchun xizmat qiladi.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tahlil'
    
    # Admin panelning yon menyusida chiqadigan nomi
    verbose_name = '📊 TAHLIL VA STATISTIKA'