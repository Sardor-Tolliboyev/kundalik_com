#!/usr/bin/env python
"""
'BilimNazoratchi' loyihasining ma'muriy topshiriqlar uchun buyruqlar satri utilitasi (manage.py).
Ushbu fayl terminal orqali serverni ishga tushirish, migratsiyalarni amalga oshirish
va boshqa boshqaruv vazifalarini bajarish uchun xizmat qiladi.
"""
import os
import sys


def main():
    """Ma'muriy topshiriqlarni ishga tushirish uchun asosiy funksiya."""

    # Loyihaning asosiy sozlamalar faylini (settings.py) tizim muhitiga (environment) tanitamiz.
    # Bizning loyihamizda u 'config' papkasi ichida joylashgan.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        # Django kutubxonasining buyruqlarni ijro etuvchi modulini yuklaymiz.
        from django.core.management import execute_from_command_line
    except ImportError as xatolik:
        # Agar Django kutubxonasi topilmasa yoki o'rnatilmagan bo'lsa,
        # tushunarli o'zbek tilida xabar chiqaramiz.
        raise ImportError(
            "Django kutubxonasi topilmadi. U o'rnatilganligiga va PYTHONPATH "
            "muhitida mavjudligiga ishonch hosil qiling. Virtual muhitni (venv) "
            "faollashtirish esingizdan chiqmadimi?"
        ) from xatolik

    # Terminaldan (buyruqlar satridan) kelgan barcha so'rovlarni (sys.argv)
    # Django boshqaruv tizimiga yuboramiz va natijani qaytaramiz.
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Fayl bevosita ishga tushirilganda (import qilinmaganda) main() funksiyasini chaqiramiz.
    main()