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
    
    # Ro'yxat sahifasida ko'rinadigan ustunlar
    list_display = ('username', 'fio_kursatish', 'rol', 'sinf_nomi', 'is_active', 'is_staff')
    # O'ng tomondagi tezkor filtrlar
    list_filter = ('rol', 'sinf', 'is_active', 'date_joined')
    # Qidiruv maydonlari
    search_fields = ('username', 'first_name', 'last_name', 'telefon')
    # Ro'yxatda tahrirlash (Tezkor amal)
    list_editable = ('rol', 'is_active')
    # Avtomatik sanalarni faqat o'qish rejimiga o'tkazish
    readonly_fields = ('last_login', 'date_joined')
    # O'qituvchi bo'lsa dars jadvalini profil ichida ko'rsatish
    inlines = [TaqsimotInline]

    # Excel tugmasi chiqishi uchun shablon
    change_list_template = "admin/hisoblar/foydalanuvchi/change_list.html"

    # --- URL SOZLAMALARI (EXCEL EXPORT UCHUN) ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download-logins/', self.admin_site.admin_view(self.export_user_logins), name='user_logins_export'),
        ]
        return custom_urls + urls

    # --- EXCELGA EKSPORT QILISH MANTIQI (Siz xohlagan 4 ta ustun bilan) ---
    def export_user_logins(self, request):
        """Barcha foydalanuvchilar ma'lumotlarini (Login va 12345678 paroli bilan) Excelga chiqarish"""
        users = Foydalanuvchi.objects.all().select_related('sinf').order_by('sinf__nomi', 'first_name')
        
        data = []
        standart_parol = "12345678"  # Tizim o'rnatgan boshlang'ich parol

        for user in users:
            data.append({
                'Ism familiyasi': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                'Login': user.username,
                'Parol': standart_parol,
                'Sinfi': user.sinf.nomi if user.sinf else "-",
                'Lavozimi': user.get_rol_display()
            })

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Foydalanuvchilar')
        
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="BilimNazoratchi_Login_Parollar.xlsx"'
        return response

    # --- QO'SHIMCHA KO'RSATISH METODLARI ---
    @admin.display(description="F.I.SH")
    def fio_kursatish(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name else obj.username

    @admin.display(description="Sinfi")
    def sinf_nomi(self, obj):
        return obj.sinf.nomi if obj.sinf else "Biriktirilmagan"
    
    # --- TAHRIRLASH SAHIFASI BLOKLARI (FIELDSETS) ---
    fieldsets = (
        ("🔐 Kirish ma'lumotlari", {'fields': ('username', 'password')}),
        ("👤 Shaxsiy ma'lumotlar", {'fields': ('first_name', 'last_name', 'email', 'telefon', 'telegram_id')}),
        ("🏫 Tizimdagi vazifa va Bog'liqlik", {'fields': ('rol', 'sinf', 'farzandi')}),
        ("🛠 Huquqlar", {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'), 'classes': ('collapse',)}),
        ("📅 Muhim sanalar", {'fields': ('last_login', 'date_joined')}),
    )

    # --- YANGI QO'SHISH SAHIFASI BLOKLARI ---
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rol', 'first_name', 'last_name', 'sinf', 'password1', 'password2'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'password' in form.base_fields:
            form.base_fields['password'].label = "Xavfsiz parol tizimi"
            form.base_fields['password'].help_text = (
            "Parol xavfsizlik yuzasidan yashirilgan. "
            "Uni o'zgartirish uchun <a href='../password/'>mana bu havolaga</a> o'ting."
        )
        return form
    
# -------------------------------------------------------------------------
# ADMIN PANEL GLOBAL BRENDING
# -------------------------------------------------------------------------
admin.site.site_header = "BILIM NAZORATCHI: BOSHQARUV MARKAZI"
admin.site.site_title = "Bilim Nazoratchi"
admin.site.index_title = "Tizim ma'lumotlarini boshqarish va monitoring"

# Standart 'Groups' bo'limini yashiramiz
if admin.site.is_registered(Group):
    admin.site.unregister(Group)