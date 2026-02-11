from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Foydalanuvchi

# -------------------------------------------------------------------------
# STANDART GURUHLARNI TOZALASH
# -------------------------------------------------------------------------
# Djangoning standart 'Groups' (Guruhlar) bo'limi ko'p hollarda ishlatilmaydi.
# Sidebar toza turishi uchun uni admin paneldan olib tashlaymiz.
admin.site.unregister(Group)


# -------------------------------------------------------------------------
# FOYDALANUVCHILARNI BOSHQARISH (ADMIN) SINFISI
# -------------------------------------------------------------------------
@admin.register(Foydalanuvchi)
class FoydalanuvchiAdmin(UserAdmin):
    """
    Foydalanuvchilarni tahrirlash, qidirish va saralash oynasi sozlamalari.
    Biz standart 'UserAdmin'dan meros olib, uni o'zbekchaga moslashtirdik.
    """

    # 1. Ro'yxat sahifasida ko'rinadigan ustunlar
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff')

    # 2. Ro'yxatning o'ng tomonidagi saralash (filtr) oynasi
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')

    # 3. Foydalanuvchini nomi, ismi yoki telefoni orqali qidirish imkoniyati
    search_fields = ('username', 'first_name', 'last_name', 'telefon')

    # 4. Faqat o'qish uchun maydonlar (Tizim avtomatik belgilaydigan sanalar)
    # Bu maydonlarni readonly_fields ga qo'shmasak, tahrirlashda xato beradi.
    readonly_fields = ('last_login', 'date_joined')

    # 5. TAHRIRLASH SAHIFASIDAGI BLOKLAR (FIELDSETS)
    # Hamma maydonlarni mantiqiy guruhlarga bo'lib chiqdik.
    fieldsets = (
        ("Kirish ma'lumotlari", {
            'fields': ('username', 'password'),
            'description': "Foydalanuvchining tizimga kirishi uchun kerakli ma'lumotlar."
        }),
        ("Shaxsiy ma'lumotlar", {
            'fields': ('first_name', 'last_name', 'email', 'telefon'),
        }),
        ("Tizimdagi roli va bog'liqlik", {
            'fields': ('rol', 'farzandi'),
            'description': "Agar roli 'Ota-ona' bo'lsa, unga o'quvchini shu yerdan biriktiring."
        }),
        ("Huquqlar va Maqom", {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
            'classes': ('collapse',),  # Bu bo'limni yashirin qildik, bosganda ochiladi
        }),
        ("Muhim sanalar", {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    # 6. PROFESSIONAL SOZLAMA: Parol maydonidagi inglizcha texnik matnlarni o'zbekchaga o'girish
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'password' in form.base_fields:
            # Rasmda ko'ringan 'algorithm', 'hash' kabi so'zlarni yashirib, o'rniga tushunarli matn qo'yamiz
            form.base_fields['password'].label = "Xavfsiz parol tizimi"
            form.base_fields['password'].help_text = (
                "Xavfsizlik yuzasidan parollar tizimda shifrlangan holatda saqlanadi. "
                "Ularni ochiq holda ko'rishning imkoni yo'q. Parolni o'zgartirish uchun "
                "<a href='../password/'>mana bu havolaga</a> o'ting."
            )
        return form


# -------------------------------------------------------------------------
# ADMIN PANEL SARLAVHALARINI BRENDING QILISH
# -------------------------------------------------------------------------
# Brauzer tabidagi nom
admin.site.site_title = "BilimNazoratchi"

# Admin panelning tepasidagi asosiy sarlavha
admin.site.site_header = "BilimNazoratchi Boshqaruv Paneli"

# Dashboardning asosiy nomi
admin.site.index_title = "Maktab ma'lumotlarini tahlil qilish va boshqarish"