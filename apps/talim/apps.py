from django.apps import AppConfig


class TalimConfig(AppConfig):
    """
    'Ta'lim' ilovasi sozlamalari.
    Ushbu bo'lim dars jadvali, baholash va sinflarni boshqaradi.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.talim"
    verbose_name = "O'QUV JARAYONI BOSHQARUVI"

