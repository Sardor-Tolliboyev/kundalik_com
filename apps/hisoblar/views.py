"""
'BilimNazoratchi' Loyihasi - Foydalanuvchi interfeysi mantiqi (Views).

Vazifasi:
1. Foydalanuvchi profil ma'lumotlarini roliga qarab yig'ish va ko'rsatish.
2. Kirish (Login) muvaffaqiyatli bo'lganda, foydalanuvchini tegishli sahifaga yo'naltirish.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
