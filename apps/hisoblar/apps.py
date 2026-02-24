from django.apps import AppConfig

class HisoblarConfig(AppConfig):
    """
    Foydalanuvchi hisoblarini boshqarish ilovasi sozlamalari.
    Ushbu klass ilovani tizimda 'Foydalanuvchi hisoblari' nomi bilan ko'rsatadi.
    """
    # Standart ID maydoni turi
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Ilovaning loyihadagi to'liq manzili
    name = 'apps.hisoblar'
    
    # Admin panelda ilovaning rasmiy o'zbekcha nomi
    verbose_name = '👤 Foydalanuvchi hisoblari'