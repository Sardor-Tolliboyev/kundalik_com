from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Sinf, Fan, Mavzu, Baho  # Dars modeli qo'shilgan bo'lsa uni ham bering

# -------------------------------------------------------------------------
# 1. ASOSIY YO'NALTIRUVCHI SAHIFA
# -------------------------------------------------------------------------
@login_required
def bosh_sahifa_view(request):
    """
    Foydalanuvchi tizimga kirganda uning roliga qarab 
    kerakli dashboardga yo'naltiruvchi asosiy funksiya.
    """
    user = request.user

    if user.rol == 'oqituvchi':
        # O'qituvchi dashboardiga o'tish
        return render(request, 'oqituvchi/dashboard.html')
    
    elif user.rol == 'oquvchi':
        # O'quvchi profiliga o'tish
        return render(request, 'oquvchi/profil.html')
    
    elif user.rol == 'admin':
        # Administrator bo'lsa, Django Admin paneliga yuborish
        return redirect('/admin/')

    # Agar roli aniqlanmagan bo'lsa, asosiy qolipni ko'rsatish
    return render(request, 'base.html')


# -------------------------------------------------------------------------
# 2. O'QITUVCHI PROFILI
# -------------------------------------------------------------------------
@login_required
def oqituvchi_profil_view(request):
    """
    O'qituvchining shaxsiy ma'lumotlari va u dars beradigan 
    fanlar ro'yxatini ko'rsatuvchi sahifa.
    """
    user = request.user
    # Xavfsizlik tekshiruvi
    # Foydalanuvchi rolini tekshirish (optional)
    if not hasattr(user, 'rol') or user.rol != 'oqituvchi':
        return redirect('talim:bosh_sahifa')

    # O'qituvchi profilini ko'rsatish uchun context
    context = {
        'user': user,
        # Qo'shimcha ma'lumotlar kerak bo'lsa shu yerda
    }
    return render(request, 'oqituvchi/profil.html', context)