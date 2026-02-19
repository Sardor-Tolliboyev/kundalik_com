from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Foydalanuvchi

# -------------------------------------------------------------------------
# 1. YANGI FOYDALANUVCHI YARATISH FORMASI
# -------------------------------------------------------------------------
class FoydalanuvchiYaratishForm(UserCreationForm):
    """
    Admin panelda yangi foydalanuvchi qo'shishda ishlatiladigan professional forma.
    Bu yerda biz 'rol' maydonini ham qo'shib ketamiz.
    """
    class Meta(UserCreationForm.Meta):
        model = Foydalanuvchi
        fields = ("username", "rol", "first_name", "last_name")

# -------------------------------------------------------------------------
# 2. FOYDALANUVCHILARNI BOSHQARISH (ADMIN KLASSI)
# -------------------------------------------------------------------------
@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(UserAdmin):
    """
    Foydalanuvchilarni tahrirlash va tahlil qilish uchun professional panel.
    """
    add_form = FoydalanuvchiYaratishForm
    form = UserChangeForm
    
    # Ro'yxat sahifasida ko'rinadigan ustunlar
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'telefon')
    list_editable = ('rol', 'is_active')
    readonly_fields = ('last_login', 'date_joined')

    # --- YANGI FOYDALANUVCHI QO'SHISH SAHIFASI (add) ---
    # MUHIM: password_confirm o'rniga password1 va password2 ishlatiladi
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rol', 'first_name', 'last_name', 'password1', 'password2'),
            'description': "Dastlab foydalanuvchining login, parol va rolini kiriting."
        }),
    )

    # --- FOYDALANUVCHINI TAHRIRLASH SAHIFASI (change) ---
    fieldsets = (
        ("🔐 Kirish ma'lumotlari", {
            'fields': ('username', 'password'),
        }),
        ("👤 Shaxsiy ma'lumotlar", {
            'fields': ('first_name', 'last_name', 'email', 'telefon'),
        }),
        ("🏫 Tizimdagi roli", {
            'fields': ('rol', 'farzandi'),
            'description': "Ota-ona bo'lsa, unga o'quvchini shu yerdan biriktiring."
        }),
        ("🛠 Huquqlar va Maqom", {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
            'classes': ('collapse',), 
        }),
        ("📅 Muhim sanalar", {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Texnik inglizcha yordamchi matnlarni o'zbekchaga o'zgartirish"""
        form = super().get_form(request, obj, **kwargs)
        if 'password' in form.base_fields:
            form.base_fields['password'].label = "Xavfsiz parol tizimi"
            form.base_fields['password'].help_text = (
                "Xavfsizlik yuzasidan parollar shifrlangan holatda saqlanadi. "
                "Parolni o'zgartirish uchun <a href='../password/'>bu yerga bosing</a>."
            )
        return form

# -------------------------------------------------------------------------
# 3. ADMIN PANEL BRANDING
# -------------------------------------------------------------------------
admin.site.site_header = "Bilim Nazoratchi: Boshqaruv Markazi"
admin.site.index_title = "Tizim ma'lumotlarini boshqarish"

# Guruhlarni o'chiramiz (agar mavjud bo'lsa)
if admin.site.is_registered(Group):
    admin.site.unregister(Group)