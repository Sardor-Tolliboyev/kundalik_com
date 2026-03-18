"""
'BilimNazoratchi' Loyihasi - Ta'lim Jarayoni Admin Sozlamalari.

Vazifasi:
1. Sinf, Fan, Taqsimot va Baholarni admin panelda boshqarish.
2. O'quvchilar ro'yxatini Exceldan ommaviy yuklash (Import).
3. Yuklangan o'quvchilar uchun Login va Parollarni Excel formatida qaytarish (Export).
"""

import io
import pandas as pd

from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html

from .models import Sinf, Fan, Taqsimot, Mavzu, Baho, Davomat
from apps.hisoblar.models import Foydalanuvchi


# -------------------------------------------------------------------------
# 1. SINF ADMINI: Excel yuklash funksiyasi bilan
# -------------------------------------------------------------------------
@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    """
    Sinflarni boshqarish va o'quvchilarni ommaviy integratsiya qilish paneli.
    """

    list_display = ('nomi', 'o_quvchilar_soni')
    search_fields = ('nomi',)

    # Excel tugmasi ko'rinishi uchun shablonni ulaymiz
    change_list_template = "admin/talim/sinf/change_list.html"

    @admin.display(description="O'quvchilar soni")
    def o_quvchilar_soni(self, sinf):
        return sinf.sinfdagi_oquvchilar.count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('excel-yuklash/', self.admin_site.admin_view(self.excel_yuklash_view), name='talim_sinf_excel_yuklash'),
            path('namuna-yuklab-olish/', self.admin_site.admin_view(self.namuna_excel_yuklab_olish), name='talim_sinf_excel_namuna'),
        ]
        return custom_urls + urls

    def excel_yuklash_view(self, request):
        """
        Excel faylni o'qib, o'quvchilarni yaratadi va
        ulardan iborat login-parol ro'yxatini qaytaradi.
        """
        if request.method == "POST":
            excel_fayl = request.FILES.get('excel_fayl')
            sinf_id = request.POST.get('sinf_id')

            if not excel_fayl or not sinf_id:
                messages.error(request, "Fayl yoki sinf tanlanmadi!")
                return redirect(".")

            try:
                jadval = pd.read_excel(excel_fayl)
                sinf_obyekti = Sinf.objects.get(id=sinf_id)

                yaratilgan_o_quvchilar = []
                standart_parol = "12345678"

                with transaction.atomic():
                    for _, qator in jadval.iterrows():
                        fio = str(qator['Ism familiyasi']).strip()
                        login = fio.replace(" ", "_").lower()[:20]

                        foydalanuvchi, created = Foydalanuvchi.objects.get_or_create(
                            username=login,
                            defaults={
                                'first_name': fio,
                                'rol': 'oquvchi',
                                'sinf': sinf_obyekti
                            }
                        )

                        if created:  # # IZOH: yangi foydalanuvchi yaratilgan bo'lsa
                            foydalanuvchi.set_password(standart_parol)
                            foydalanuvchi.save()

                        yaratilgan_o_quvchilar.append({
                            'F.I.SH': fio,
                            'Login (Username)': login,
                            'Parol': standart_parol,
                            'Sinfi': sinf_obyekti.nomi
                        })

                natija_df = pd.DataFrame(yaratilgan_o_quvchilar)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    natija_df.to_excel(writer, index=False, sheet_name='Oquvchi_Loginlari')

                output.seek(0)
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="Yangi_Loginlar_{sinf_obyekti.nomi}.xlsx"'
                messages.success(request, f"{len(yaratilgan_o_quvchilar)} ta o'quvchi bazaga qo'shildi va loginlar fayli tayyorlandi.")
                return response

            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
                return redirect(".")

        return render(request, "admin/excel_import.html", {"sinflar": Sinf.objects.all()})

    def namuna_excel_yuklab_olish(self, request):
        """
        Excel import uchun namuna faylni generatsiya qilib yuklab beradi.

        # IZOH: Import funksiyasi `Ism familiyasi` ustunini o'qiydi, shuning uchun namuna ham shu formatda.
        """
        # # IZOH: Namuna ko'rinishi foydalanuvchiga tushunarli bo'lishi uchun "Sinf" ustunini ham qo'shamiz.
        # Import jarayonida esa sinf admin forma orqali tanlanadi (excel'dagi "Sinf" ustuni ixtiyoriy).
        namuna_df = pd.DataFrame(
            [
                {"Ism familiyasi": "Ali Valiyev", "Sinf": "5-sinf"},
                {"Ism familiyasi": "Valiyeva Malika", "Sinf": "5-sinf"},
                {"Ism familiyasi": "G'aniyev Sardor", "Sinf": "5-sinf"},
            ],
            columns=["Ism familiyasi", "Sinf"],
        )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            namuna_df.to_excel(writer, index=False, sheet_name="Namuna")

        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="oquvchi_namuna.xlsx"'
        return response


# -------------------------------------------------------------------------
# 2. BOSHQA MODELLAR ADMIN SOZLAMALARI
# -------------------------------------------------------------------------
@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)


@admin.register(Taqsimot)
class TaqsimotAdmin(admin.ModelAdmin):
    """Qaysi o'qituvchi qaysi sinfga dars o'tishini boshqarish"""
    list_display = ('sinf', 'fan', 'oqituvchi', 'kun', 'soat')
    list_filter = ('sinf', 'fan', 'oqituvchi', 'kun')
    search_fields = ('oqituvchi__username', 'oqituvchi__first_name', 'oqituvchi__last_name', 'sinf__nomi', 'fan__nomi')
    list_select_related = ('sinf', 'fan', 'oqituvchi')

    def get_model_perms(self, request):
        """
        # IZOH: Admin yon menyusida "Dars taqsimoti" bo'limi ko'rinmasin.
        Jadvalni boshqarish `Dars jadvali` sahifasi orqali amalga oshiriladi.
        """
        return {}


@admin.register(Mavzu)
class MavzuAdmin(admin.ModelAdmin):
    """Kundalik dars mavzulari monitoringi"""
    list_display = ('sana', 'taqsimot', 'mavzu_nomi')
    list_filter = ('sana', 'taqsimot__sinf', 'taqsimot__fan')
    date_hierarchy = 'sana'
    search_fields = ('mavzu_nomi', 'taqsimot__sinf__nomi', 'taqsimot__fan__nomi', 'taqsimot__oqituvchi__username')
    list_select_related = ('taqsimot', 'taqsimot__sinf', 'taqsimot__fan', 'taqsimot__oqituvchi')


@admin.register(Baho)
class BahoAdmin(admin.ModelAdmin):
    """O'quvchilarning baholarini nazorat qilish"""
    list_display = ('oquvchi', 'fan_nomi', 'qiymati', 'sana_korish')
    list_filter = ('qiymati', 'mavzu__taqsimot__fan')
    search_fields = ('oquvchi__username', 'oquvchi__first_name', 'oquvchi__last_name')
    list_select_related = ('oquvchi', 'mavzu', 'mavzu__taqsimot', 'mavzu__taqsimot__fan')

    @admin.display(description="Fan")
    def fan_nomi(self, baho):
        return baho.mavzu.taqsimot.fan.nomi

    @admin.display(description="Sana")
    def sana_korish(self, baho):
        return baho.mavzu.sana


@admin.register(Davomat)
class DavomatAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'mavzu', 'keldi_vizual')
    list_filter = ('keldi', 'mavzu__sana')
    search_fields = ('oquvchi__username', 'oquvchi__first_name', 'oquvchi__last_name', 'mavzu__mavzu_nomi')
    list_select_related = ('oquvchi', 'mavzu', 'mavzu__taqsimot', 'mavzu__taqsimot__fan')

    @admin.display(description="Ishtirok")
    def keldi_vizual(self, davomat):
        # Admin jadvalida davomat holatini ko‘rinarli “badge” ko‘rinishida chiqaramiz.
        # Eslatma: `format_html()`da kamida bitta `args/kwargs` bo‘lishi shart.
        if davomat.keldi:
            return format_html(
                '<span style="display:inline-block;padding:3px 10px;border-radius:999px;'
                'background:#dcfce7;color:#166534;font-weight:900;">{label}</span>',
                label="Keldi",
            )
        return format_html(
            '<span style="display:inline-block;padding:3px 10px;border-radius:999px;'
            'background:#fee2e2;color:#991b1b;font-weight:900;">{label}</span>',
            label="Kelmadi",
        )
