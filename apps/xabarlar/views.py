"""
'BilimNazoratchi' Loyihasi - Bildirishnomalar va Xabarlar mantiqi (Views).

Vazifasi:
1. Foydalanuvchiga kelgan barcha bildirishnomalarni ro'yxat ko'rinishida chiqarish.
2. Xabarni batafsil ko'rsatish va uni avtomatik ravishda 'O'qilgan' holatiga o'tkazish.
3. Yangi (o'qilmagan) xabarlar sonini hisoblab borish.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ogohlantirish

# -------------------------------------------------------------------------
# 1. BILDIRISHNOMALAR RO'YXATI VIEW
# -------------------------------------------------------------------------
@login_required
def xabarlar_ruyxati_view(request):
    """
    Tizimga kirgan foydalanuvchiga (Ota-ona yoki O'qituvchi) 
    tegishli barcha bildirishnomalar ro'yxatini ko'rsatuvchi sahifa.
    """
    foydalanuvchi = request.user
    
    # Faqat joriy foydalanuvchiga yuborilgan xabarlarni bazadan olamiz
    # select_related ishlatib, qabul qiluvchi ma'lumotlarini ham optimallashtiramiz
    xabarlar_toplami = Ogohlantirish.objects.filter(kimga=foydalanuvchi).order_by('-yaratilgan_vaqt')
    
    # O'qilmagan (yangi) xabarlar sonini hisoblaymiz
    yangi_xabarlar_soni = xabarlar_toplami.filter(oqilgan=False).count()

    kontekst = {
        'xabarlar': xabarlar_toplami,
        'yangi_xabarlar_soni': yangi_xabarlar_soni,
        'sahifa_nomi': "Mening bildirishnomalarim"
    }
    
    return render(request, 'xabarlar/ruyxat.html', kontekst)


# -------------------------------------------------------------------------
# 2. XABARNI O'QISH VA BATAFSIL KO'RISH VIEW
# -------------------------------------------------------------------------
@login_required
def xabarni_oqish_view(request, xabar_id):
    """
    Xabar ustiga bosilganda uni to'liq ko'rsatish va 
    tizimda 'O'qilgan' (read) deb qayd etish funksiyasi.
    """
    foydalanuvchi = request.user
    
    # Xabarni qidiramiz. 
    # Xavfsizlik: Faqat xabar egasi (kimga=user) uni ko'ra olishini ta'minlaymiz.
    xabar = get_object_or_404(Ogohlantirish, id=xabar_id, kimga=foydalanuvchi)
    
    # Agar xabar hali o'qilmagan bo'lsa, uni o'qilgan deb belgilaymiz
    if not xabar.oqilgan:
        xabar.oqilgan = True
        xabar.save() # Bazada holatni yangilaymiz

    kontekst = {
        'xabar': xabar,
        'sahifa_nomi': xabar.sarlavha
    }
    
    return render(request, 'xabarlar/batafsil.html', kontekst)


# -------------------------------------------------------------------------
# 3. BARCHA XABARLARNI O'QILGAN DEB BELGILASH (Qo'shimcha qulaylik)
# -------------------------------------------------------------------------
@login_required
def hammasini_oqilgan_qilish_view(request):
    """
    Foydalanuvchining barcha yangi xabarlarini bitta bosish bilan 
    'o'qilgan' holatiga o'tkazuvchi tezkor funksiya.
    """
    Ogohlantirish.objects.filter(kimga=request.user, oqilgan=False).update(oqilgan=True)
    
    messages.success(request, "Barcha xabarlar o'qilgan deb belgilandi.")
    return redirect('xabarlar:xabarlar_ruyxati')