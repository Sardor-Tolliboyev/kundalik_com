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
    user = request.user
    
    # Barcha rollar uchun umumiy ma'lumotlar
    kontekst = {
        'foydalanuvchi': user,
        'rol_nomi': user.get_rol_display(), # 'oquvchi' -> 'O'quvchi' ko'rinishida olish
    }
    
    # --- ROLGA QARAB QO'SHIMCHA MA'LUMOTLARNI YIG'ISH ---

    # A) Agar foydalanuvchi O'QUVCHI bo'lsa
    if user.rol == 'oquvchi':
        # Sinf ma'lumotini tekshiramiz
        kontekst['sinf_nomi'] = user.sinf.nomi if user.sinf else "Sinfga biriktirilmagan"
        
    # B) Agar foydalanuvchi OTA-ONA bo'lsa
    elif user.rol == 'ota_ona':
        # Biriktirilgan farzandi borligini tekshiramiz
        if user.farzandi:
            kontekst['farzand_fio'] = user.farzandi.get_full_name() or user.farzandi.username
            kontekst['farzand_sinfi'] = user.farzandi.sinf.nomi if user.farzandi.sinf else "Noma'lum"
        else:
            kontekst['farzand_fio'] = "Farzand biriktirilmagan"

    # D) Agar foydalanuvchi O'QITUVCHI bo'lsa
    elif user.rol == 'oqituvchi':
        # O'qituvchiga tegishli darslar sonini hisoblash mumkin
        kontekst['darslar_soni'] = user.oqituvchi_darslari.count()

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
    user = request.user
    
    # 1. O'qituvchi bo'lsa - Sinf tanlash dashboardiga
    if user.rol == 'oqituvchi':
        messages.success(request, f"Xush kelibsiz, {user.first_name}! Ish faoliyatingizda muvaffaqiyatlar tilaymiz.")
        return redirect('talim:oqituvchi_dashboard')
        
    # 2. O'quvchi bo'lsa - Shaxsiy natijalar profiliga
    elif user.rol == 'oquvchi':
        messages.info(request, f"Salom, {user.first_name}. Bugungi natijalaringni ko'rishga tayyormisan?")
        return redirect('talim:oquvchi_profil')
        
    # 3. Ota-ona bo'lsa - Farzandining nazorat sahifasiga
    elif user.rol == 'ota_ona':
        return redirect('talim:ota_ona_view')
        
    # 4. Administrator bo'lsa - To'g'ridan-to'g'ri boshqaruv paneliga
    elif user.rol == 'admin' or user.is_superuser:
        return redirect('/admin/')
    
    # Agar roli aniqlanmagan yoki xato bo'lsa, asosiy sahifaga qaytaramiz
    return redirect('talim:bosh_sahifa')