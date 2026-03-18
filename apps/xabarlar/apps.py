from django.apps import AppConfig


class XabarlarConfig(AppConfig):
    """
    'Xabarlar' ilovasi sozlamalari.
    Ushbu bo'lim tizimdagi barcha bildirishnomalar va ogohlantirishlarni boshqaradi.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.xabarlar"
    verbose_name = "BILDIRISHNOMALAR VA ALOQA"

