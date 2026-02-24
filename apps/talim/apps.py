from django.apps import AppConfig

class TalimConfig(AppConfig):
    """
    'Talim' ilovasi sozlamalari. 
    Ushbu bo'lim dars jadvali, baholash va sinflarni boshqaradi.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.talim'
    
    # Admin panelda ilovaning o'zbekcha nomi
    verbose_name = '📚 O‘QUV JARAYONI BOSHQARUVI'