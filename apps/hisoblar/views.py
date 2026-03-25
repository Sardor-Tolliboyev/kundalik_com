"""
'BilimNazoratchi' Loyihasi - Foydalanuvchi interfeysi mantiqi (Views).

Vazifasi:
1. Foydalanuvchi profil ma'lumotlarini roliga qarab yig'ish va ko'rsatish.
2. Kirish (Login) muvaffaqiyatli bo'lganda, foydalanuvchini tegishli sahifaga yo'naltirish.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import ShaxsiyProfilTahrirForm

# -------------------------------------------------------------------------
# 1. SHAXSIY PROFIL VIEW
# -------------------------------------------------------------------------
@login_required
def shaxsiy_profil_view(request):
    """
    Tizimga kirgan foydalanuvchining shaxsiy ma'lumotlarini 
    va uning roliga oid mantiqiy bog'liqliklarni ko'rsatuvchi funksiya.
    """
    foydalanuvchi = request.user
    
    # Barcha rollar uchun umumiy ma'lumotlar
    kontekst = {
        'foydalanuvchi': foydalanuvchi,
        'rol_nomi': foydalanuvchi.get_rol_display(), # 'oquvchi' -> 'O'quvchi' ko'rinishida olish
    }
    
    # --- ROLGA QARAB QO'SHIMCHA MA'LUMOTLARNI YIG'ISH ---

    # A) Agar foydalanuvchi O'QUVCHI bo'lsa
    if foydalanuvchi.rol == 'oquvchi':
        # Sinf ma'lumotini tekshiramiz
        kontekst['sinf_nomi'] = foydalanuvchi.sinf.nomi if foydalanuvchi.sinf else "Sinfga biriktirilmagan"
        
    # B) Agar foydalanuvchi OTA-ONA bo'lsa
    elif foydalanuvchi.rol == 'ota_ona':
        # Biriktirilgan farzandi borligini tekshiramiz
        if foydalanuvchi.farzandi:
            kontekst['farzand_fio'] = foydalanuvchi.farzandi.get_full_name() or foydalanuvchi.farzandi.username
            kontekst['farzand_sinfi'] = foydalanuvchi.farzandi.sinf.nomi if foydalanuvchi.farzandi.sinf else "Noma'lum"
        else:
            kontekst['farzand_fio'] = "Farzand biriktirilmagan"

    # D) Agar foydalanuvchi O'QITUVCHI bo'lsa
    elif foydalanuvchi.rol == 'oqituvchi':
        # O'qituvchiga tegishli darslar sonini hisoblash mumkin
        kontekst['darslar_soni'] = foydalanuvchi.oqituvchi_darslari.count()

    # Natijani eMaktab uslubidagi profil shabloniga yuboramiz
    return render(request, 'registration/profile.html', kontekst)


# -------------------------------------------------------------------------
# 2. MANTIQIY YO'NALTIRISH (SMART REDIRECT)
# -------------------------------------------------------------------------
@login_required
def login_redirect_view(request):
    """
    Foydalanuvchi login-parolini terib kirganda ishga tushadi.
    Vazifasi: Foydalanuvchini 'shartta' o'zining ish stoliga yuborish.
    """
    foydalanuvchi = request.user
    
    # 1. O'qituvchi bo'lsa - Sinf tanlash dashboardiga
    if foydalanuvchi.rol == 'oqituvchi':
        messages.success(request, f"Xush kelibsiz, {foydalanuvchi.first_name}! Ish faoliyatingizda muvaffaqiyatlar tilaymiz.")
        return redirect('talim:oqituvchi_dashboard')
        
    # 2. O'quvchi bo'lsa - Shaxsiy natijalar profiliga
    elif foydalanuvchi.rol == 'oquvchi':
        messages.info(request, f"Salom, {foydalanuvchi.first_name}. Bugungi natijalaringni ko'rishga tayyormisan?")
        return redirect('talim:oquvchi_profil')
        
    # 3. Ota-ona bo'lsa - Farzandining nazorat sahifasiga
    elif foydalanuvchi.rol == 'ota_ona':
        return redirect('talim:ota_ona_view')
        
    # 4. Administrator bo'lsa - To'g'ridan-to'g'ri boshqaruv paneliga
    elif foydalanuvchi.rol == 'admin' or foydalanuvchi.is_superuser:
        return redirect('/admin/')
    
    # Agar roli aniqlanmagan yoki xato bo'lsa, asosiy sahifaga qaytaramiz
    return redirect('talim:bosh_sahifa')


# -------------------------------------------------------------------------
# 3. SHAXSIY PROFILNI TAHRIRLASH (HAMMA FOYDALANUVCHILAR UCHUN)
# -------------------------------------------------------------------------
@login_required
def shaxsiy_profil_tahrir_view(request):
    """
    Foydalanuvchi o'zining shaxsiy ma'lumotlarini (login emas) va parolini tahrirlaydi.

    # IZOH:
    # - Bu sahifa uchun alohida "huquq" talab qilinmaydi, chunki foydalanuvchi faqat o'zini tahrirlaydi.
    # - Admin panelga kirish shart emas: o'quvchi/ota-ona/o'qituvchi ham o'zini yangilay oladi.
    """
    foydalanuvchi = request.user

    profil_forma = ShaxsiyProfilTahrirForm(instance=foydalanuvchi)
    parol_forma = PasswordChangeForm(user=foydalanuvchi)

    # # IZOH: Bootstrap bilan mos ko'rinish uchun parol formasi fieldlariga class beramiz.
    for f in parol_forma.fields.values():
        f.widget.attrs.setdefault("class", "form-control")

    # # IZOH: Django `PasswordChangeForm` ayrim label/help_textlarni inglizcha chiqarishi mumkin.
    # Bu yerda i18n'ga kirmasdan, oddiy usulda o'zbekchalashtiramiz.
    if "old_password" in parol_forma.fields:
        parol_forma.fields["old_password"].label = "Avvalgi parol"
    if "new_password1" in parol_forma.fields:
        parol_forma.fields["new_password1"].label = "Yangi parol"
        parol_forma.fields["new_password1"].help_text = (
            "<ul>"
            "<li>Parolingiz shaxsiy ma'lumotlaringizga juda o'xshash bo'lmasin.</li>"
            "<li>Parol kamida 8 ta belgidan iborat bo'lishi kerak.</li>"
            "<li>Parol juda ommabop parol bo'lmasin.</li>"
            "<li>Parol faqat raqamlardan iborat bo'lmasin.</li>"
            "</ul>"
        )
    if "new_password2" in parol_forma.fields:
        parol_forma.fields["new_password2"].label = "Yangi parolni tasdiqlash"

    if request.method == "POST":
        if "profil_saqlash" in request.POST:
            profil_forma = ShaxsiyProfilTahrirForm(request.POST, instance=foydalanuvchi)
            if profil_forma.is_valid():
                profil_forma.save()
                messages.success(request, "Shaxsiy ma'lumotlaringiz muvaffaqiyatli saqlandi.")
                return redirect("hisoblar:shaxsiy_profil_tahrir")

        if "parol_saqlash" in request.POST:
            parol_forma = PasswordChangeForm(user=foydalanuvchi, data=request.POST)
            for f in parol_forma.fields.values():
                f.widget.attrs.setdefault("class", "form-control")

            if "old_password" in parol_forma.fields:
                parol_forma.fields["old_password"].label = "Avvalgi parol"
            if "new_password1" in parol_forma.fields:
                parol_forma.fields["new_password1"].label = "Yangi parol"
                parol_forma.fields["new_password1"].help_text = (
                    "<ul>"
                    "<li>Parolingiz shaxsiy ma'lumotlaringizga juda o'xshash bo'lmasin.</li>"
                    "<li>Parol kamida 8 ta belgidan iborat bo'lishi kerak.</li>"
                    "<li>Parol juda ommabop parol bo'lmasin.</li>"
                    "<li>Parol faqat raqamlardan iborat bo'lmasin.</li>"
                    "</ul>"
                )
            if "new_password2" in parol_forma.fields:
                parol_forma.fields["new_password2"].label = "Yangi parolni tasdiqlash"
            if parol_forma.is_valid():
                parol_forma.save()
                update_session_auth_hash(request, foydalanuvchi)
                messages.success(request, "Parolingiz muvaffaqiyatli yangilandi.")
                return redirect("hisoblar:shaxsiy_profil_tahrir")

    kontekst = {
        "profil_forma": profil_forma,
        "parol_forma": parol_forma,
    }
    return render(request, "registration/profil_tahrirlash.html", kontekst)
