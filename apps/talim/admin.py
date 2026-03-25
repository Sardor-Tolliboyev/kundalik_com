"""
'BilimNazoratchi' Loyihasi - Ta'lim Jarayoni Admin Sozlamalari.

Vazifasi:
1. Sinf, Fan, Taqsimot va Baholarni admin panelda boshqarish.
2. O'quvchilar ro'yxatini Exceldan ommaviy yuklash (Import).
3. Yuklangan o'quvchilar uchun Login va Parollarni Excel formatida qaytarish (Export).
"""

import io
import pandas as pd
import re

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

                # # IZOH: Excel'da ota-ona F.I.SH ustuni turli nomlarda kelishi mumkin.
                # Userlar ko'pincha "ota" / "otasi" deb yozib yuboradi, shuning uchun ikkalasini ham qabul qilamiz.
                ota_ona_ustun_nomlari = [
                    "ota yoki onasi ism familiyasi",
                    "Ota yoki onasi ism familiyasi",
                    "otasi yoki onasi ism familiyasi",
                    "Otasi yoki onasi ism familiyasi",
                    "Ota/ona ism familiyasi",
                    "Ota-ona ism familiyasi",
                    "Ota onasi ism familiyasi",
                    "Ota-ona F.I.SH",
                    "Ota-ona FIO",
                    "Ota-ona",
                ]

                def _norm_matn(matn: str) -> str:
                    x = str(matn or "").strip().lower()
                    x = x.replace(".", " ").replace("/", " ").replace("-", " ").replace("_", " ")
                    x = re.sub(r"\s+", " ", x)
                    return x

                def ustun_top(ustunlar, nomlar):
                    ustunlar_norm = {_norm_matn(x): str(x) for x in ustunlar}
                    for nom in nomlar:
                        kalit = _norm_matn(nom)
                        if kalit in ustunlar_norm:
                            return ustunlar_norm[kalit]
                    return None

                ota_ona_ustuni = ustun_top(jadval.columns, ota_ona_ustun_nomlari)

                if ota_ona_ustuni is None:
                    # # IZOH: Ustun nomi aynan mos kelmasa ham, ma'nosiga qarab topishga harakat qilamiz.
                    for col in jadval.columns:
                        n = _norm_matn(col)
                        if "ota" in n and ("ona" in n or "onasi" in n) and ("ism" in n or "familiya" in n or "fio" in n or "fish" in n):
                            ota_ona_ustuni = str(col)
                            break

                def fio_ajrat(fio_matn: str):
                    """
                    F.I.SH'ni (Ism Familiya) ajratish.

                    # IZOH: Oldingi importda fio to'liq `first_name`ga yozilgan.
                    # Endi chiroyliroq bo'lishi uchun `first_name` va `last_name`ga bo'lamiz.
                    """
                    qismlar = [x for x in (fio_matn or "").strip().split(" ") if x]
                    if not qismlar:
                        return "", ""
                    if len(qismlar) == 1:
                        return qismlar[0], ""
                    return " ".join(qismlar[:-1]), qismlar[-1]

                def login_yasash(fio_matn: str):
                    """
                    F.I.SH asosida login tayyorlash va unikallikni ta'minlash.

                    # IZOH: Django username uchun xavfsiz belgilarga keltiramiz va 20 belgidan oshirmaymiz.
                    """
                    xom = (fio_matn or "").strip().lower()
                    xom = xom.replace("’", "").replace("'", "").replace("`", "")
                    xom = re.sub(r"\s+", "_", xom)
                    xom = re.sub(r"[^a-z0-9_]+", "", xom)
                    if not xom:
                        xom = "user"

                    asos = xom[:20]
                    kandidat = asos
                    raqam = 1
                    while Foydalanuvchi.objects.filter(username=kandidat).exists():
                        raqam += 1
                        suff = str(raqam)
                        kesma = (asos[: max(1, 20 - (len(suff) + 1))]).rstrip("_")
                        kandidat = f"{kesma}_{suff}"
                    return kandidat

                with transaction.atomic():
                    for _, qator in jadval.iterrows():
                        fio_qiymat = qator.get("Ism familiyasi", "")
                        fio = "" if pd.isna(fio_qiymat) else str(fio_qiymat).strip()
                        if not fio:
                            continue

                        login = login_yasash(fio)
                        ism, familiya = fio_ajrat(fio)

                        foydalanuvchi, created = Foydalanuvchi.objects.get_or_create(
                            username=login,
                            defaults={
                                'first_name': ism,
                                'last_name': familiya,
                                'rol': 'oquvchi',
                                'sinf': sinf_obyekti,
                            },
                        )

                        if created:  # # IZOH: yangi foydalanuvchi yaratilgan bo'lsa
                            foydalanuvchi.set_password(standart_parol)
                            foydalanuvchi.save()

                        # Ota-ona yaratish (ixtiyoriy ustun)
                        ota_ona_fio = ""
                        ota_ona_login = "-"
                        ota_ona_parol = "-"
                        if ota_ona_ustuni:
                            ota_ona_qiymat = qator.get(ota_ona_ustuni, "")
                            ota_ona_fio = "" if pd.isna(ota_ona_qiymat) else str(ota_ona_qiymat).strip()

                        # Avvaldan ota-ona biriktirilgan bo'lsa, loginini chiqaramiz (parolni taxmin qilmaymiz).
                        mavjud_ota_onalar = list(foydalanuvchi.ota_onasi.all())
                        if mavjud_ota_onalar and not ota_ona_fio:
                            ota_ona_login = "; ".join([x.username for x in mavjud_ota_onalar if x.username]) or "-"

                        if ota_ona_fio:
                            ota_ism, ota_fam = fio_ajrat(ota_ona_fio)
                            ota_ana_fio_norm = " ".join([ota_ism, ota_fam]).strip().lower()

                            # # IZOH: Bir xil F.I.SH bilan ota-ona allaqachon bog'langan bo'lsa, takror yaratmaymiz.
                            moslari = [
                                x for x in mavjud_ota_onalar
                                if (" ".join([x.first_name or "", x.last_name or ""]).strip().lower() == ota_ana_fio_norm)
                            ]
                            if moslari:
                                ota_ona_login = "; ".join([x.username for x in moslari if x.username]) or "-"
                            else:
                                ota_ona_login = login_yasash(ota_ona_fio)
                                ota_ona_user = Foydalanuvchi.objects.create(
                                    username=ota_ona_login,
                                    first_name=ota_ism,
                                    last_name=ota_fam,
                                    rol="ota_ona",
                                    farzandi=foydalanuvchi,
                                    # # IZOH: ota-onani ham sinfga bog'lab qo'yamiz (filtr uchun qulay).
                                    sinf=sinf_obyekti,
                                )
                                ota_ona_user.set_password(standart_parol)
                                ota_ona_user.save()
                                ota_ona_parol = standart_parol

                        yaratilgan_o_quvchilar.append({
                            'F.I.SH': fio,
                            'Login (Username)': login,
                            'Parol': standart_parol,
                            'Sinfi': sinf_obyekti.nomi,
                            "Ota-ona F.I.SH": ota_ona_fio or "-",
                            "Ota-ona login": ota_ona_login,
                            "Ota-ona parol": ota_ona_parol,
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
                {"Ism familiyasi": "Ali Valiyev", "Sinf": "5-sinf", "Ota yoki onasi ism familiyasi": "Salimov Ali"},
                {"Ism familiyasi": "Valiyeva Malika", "Sinf": "5-sinf", "Ota yoki onasi ism familiyasi": "Qurashev Joni"},
                {"Ism familiyasi": "G'aniyev Sardor", "Sinf": "5-sinf", "Ota yoki onasi ism familiyasi": "Sadriyeva Guli"},
            ],
            columns=["Ism familiyasi", "Sinf", "Ota yoki onasi ism familiyasi"],
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
