# apps/talim/apps.py

from django.apps import AppConfig


class TahlilConfig(AppConfig):
    name = 'apps.tahlil'   # <--- FAQAT tahlil bo'lishi shart
    label = 'tahlil'

    verbose_name = 'O‘quv jarayoni boshqaruvi'