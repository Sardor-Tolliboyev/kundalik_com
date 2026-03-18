"""
'BilimNazoratchi' Loyihasi - Foydalanuvchilar boshqaruv markazi.
Vazifasi:
1. Foydalanuvchilarni roli va sinfi bo'yicha boshqarish.
2. O'qituvchi profilida uning dars jadvalini (Taqsimot) ko'rish va tahrirlash.
3. Barcha foydalanuvchilar login-parollarini Excelga eksport qilish.
"""

import pandas as pd
import io
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.http import HttpResponse
from django.urls import path

# Modellarimizni import qilamiz
from .models import Foydalanuvchi
from apps.talim.models import Taqsimot  # DarsJadvali o'rniga Taqsimot ishlatiladi

# -------------------------------------------------------------------------
# 1. YANGI FOYDALANUVCHI YARATISH FORMASI
# -------------------------------------------------------------------------
class FoydalanuvchiYaratishForm(UserCreationForm):
    """
    Admin panelda yangi foydalanuvchi qo'shish oynasi uchun forma.
    Bu yerda 'rol' va 'sinf' maydonlarini majburiy yoki ixtiyoriy ko'rsatamiz.
    """

    class Meta(UserCreationForm.Meta):
        model = Foydalanuvchi
        fields = ("username", "rol", "first_name", "last_name", "sinf")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].required = True


# -------------------------------------------------------------------------
# 2. DARSLAR TAQSIMOTI INLINE (O'qituvchi profilida darslarini ko'rish)
# -------------------------------------------------------------------------
class TaqsimotInline(admin.TabularInline):
    """
    O'qituvchini tahrirlash sahifasida unga dars (sinf va fan)
    biriktirish imkonini beruvchi ichki jadval (Inline).
    """

    model = Taqsimot
    extra = 1  # Bo'sh qatorlar soni
    verbose_name = "Biriktirilgan dars"
    verbose_name_plural = "O'qituvchining dars jadvali"
    fk_name = "oqituvchi"


# -------------------------------------------------------------------------
# 3. ASOSIY FOYDALANUVCHILAR BOSHQARUVI (ADMIN)
# -------------------------------------------------------------------------
@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(UserAdmin):
    """
    Foydalanuvchilar ro'yxatini boshqarish va login-parollarni
    Excelga eksport qilish uchun professional boshqaruv paneli.
    """

    add_form = FoydalanuvchiYaratishForm
    form = UserChangeForm

    list_display = ('username', 'fio_kursatish', 'rol', 'sinf_nomi', 'is_active', 'is_staff')
    list_filter = ('rol', 'sinf', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'telefon')
    list_editable = ('rol', 'is_active')
    readonly_fields = ('last_login', 'date_joined')
    inlines = [TaqsimotInline]

    change_list_template = "admin/hisoblar/foydalanuvchi/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download-logins/', self.admin_site.admin_view(self.export_user_logins), name='user_logins_export'),
        ]
        return custom_urls + urls

    def get_inline_instances(self, request, obj=None):
        """
        Inline (O'qituvchining dars jadvali) faqat o'qituvchi roli uchun ko'rinsin.

        # IZOH: Admin foydalanuvchi tahrirlash sahifasida "O'qituvchining dars jadvali"
        # blokini faqat `rol='oqituvchi'` bo'lganda chiqaramiz. Boshqa rollarda bu bo'lim
        # keraksiz va chalkashlik keltiradi.
        """
        if obj is None:
            return []
        if getattr(obj, "rol", "") != "oqituvchi":
            return []
        return super().get_inline_instances(request, obj=obj)

    def export_user_logins(self, request):
        """Barcha foydalanuvchilar ma'lumotlarini (Login va 12345678 paroli bilan) Excelga chiqarish"""
        foydalanuvchilar = (
            Foydalanuvchi.objects.all()
            .select_related('sinf')
            .order_by('sinf__nomi', 'first_name')
        )

        malumotlar = []
        standart_parol = "12345678"

        for foydalanuvchi in foydalanuvchilar:
            # # IZOH: Excel ustun nomlarini o'zgartirmaymiz (format bir xil bo'lib qoladi).
            malumotlar.append({
                'Ism familiyasi': f"{foydalanuvchi.first_name} {foydalanuvchi.last_name}" if foydalanuvchi.first_name else foydalanuvchi.username,
                'Login': foydalanuvchi.username,
                'Parol': standart_parol,
                'Sinfi': foydalanuvchi.sinf.nomi if foydalanuvchi.sinf else "-",
                'Lavozimi': foydalanuvchi.get_rol_display()
            })

        jadval_df = pd.DataFrame(malumotlar)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            jadval_df.to_excel(writer, index=False, sheet_name='Foydalanuvchilar')

        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="BilimNazoratchi_Login_Parollar.xlsx"'
        return response

    @admin.display(description="F.I.SH")
    def fio_kursatish(self, foydalanuvchi):
        return f"{foydalanuvchi.first_name} {foydalanuvchi.last_name}" if foydalanuvchi.first_name else foydalanuvchi.username

    @admin.display(description="Sinfi")
    def sinf_nomi(self, foydalanuvchi):
        return foydalanuvchi.sinf.nomi if foydalanuvchi.sinf else "Biriktirilmagan"

    fieldsets = (
        ("Kirish ma'lumotlari", {'fields': ('username', 'password')}),
        ("Shaxsiy ma'lumotlar", {'fields': ('first_name', 'last_name', 'email', 'telefon', 'telegram_id')}),
        ("Tizimdagi vazifa va bog'liqlik", {'fields': ('rol', 'sinf', 'farzandi')}),
        ("Huquqlar", {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'), 'classes': ('collapse',)}),
        ("Muhim sanalar", {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rol', 'first_name', 'last_name', 'sinf', 'password1', 'password2'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # # IZOH: Django'ning standart User maydonlarida (is_active, is_staff, ...)
        # inglizcha label/help_textlar kelib qolmasligi uchun ularni shu yerning o'zida
        # to'liq o'zbekchalashtiramiz (migratsiyasiz, DBga tegmaydi).
        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].label = "Faol"
            form.base_fields['is_active'].help_text = (
                "Belgilansa foydalanuvchi tizimdan foydalanadi. "
                "O'chirish o'rniga faolligini olib tashlash tavsiya etiladi."
            )

        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = "Xodim holati"
            form.base_fields['is_staff'].help_text = "Belgilansa foydalanuvchi admin panelga kira oladi."

        if 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].label = "Superadmin holati"
            form.base_fields['is_superuser'].help_text = (
                "Belgilansa foydalanuvchi barcha huquqlarga ega bo'ladi (alohida ruxsat berilmasa ham)."
            )

        if 'user_permissions' in form.base_fields:
            form.base_fields['user_permissions'].label = "Foydalanuvchi huquqlari"
            form.base_fields['user_permissions'].help_text = (
                "Quyidagi ro'yxatdan kerakli huquqlarni tanlab, o'ng tomonga o'tkazing."
            )

        if 'last_login' in form.base_fields:
            form.base_fields['last_login'].label = "Oxirgi kirish"

        if 'date_joined' in form.base_fields:
            form.base_fields['date_joined'].label = "Ro'yxatdan o'tgan sana"

        if 'password' in form.base_fields:
            form.base_fields['password'].label = "Xavfsiz parol tizimi"
            form.base_fields['password'].help_text = (
                "Parol xavfsizlik yuzasidan yashirilgan. "
                "Uni o'zgartirish uchun <a href='../password/'>mana bu havolaga</a> o'ting."
            )
        return form


admin.site.site_header = "BILIM NAZORATCHI: BOSHQARUV MARKAZI"
admin.site.site_title = "Bilim Nazoratchi"
admin.site.index_title = "Tizim ma'lumotlarini boshqarish va monitoring"

if admin.site.is_registered(Group):
    admin.site.unregister(Group)
