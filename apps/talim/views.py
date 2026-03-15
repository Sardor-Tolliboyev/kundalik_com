"""
'BilimNazoratchi' Loyihasi - Ta'lim Jarayoni Mantiqiy Markazi (Views).

Vazifasi:
1. Foydalanuvchini roliga qarab tegishli dashboardga yo'naltirish.
2. O'qituvchi uchun sinflar ro'yxati va mukkammal elektron jurnalni shakllantirish.
3. Baholash va Davomatni (yo'qlama) saqlash mantiqini boshqarish.
4. O'quvchi va ota-onalar uchun tahliliy ma'lumotlarni yig'ish.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date

# Loyihamiz modellarini import qilamiz
from .models import Sinf, Fan, Taqsimot, Mavzu, Baho, Davomat
from apps.hisoblar.models import Foydalanuvchi

# -------------------------------------------------------------------------
# 1. LANDING VA ASOSIY YO'NALTIRUVCHI
# -------------------------------------------------------------------------

def landing_view(request):
    """Tizimga kirmagan mehmonlar uchun tanishtiruv sahifasi (Landing Page)"""
    if request.user.is_authenticated:
        return redirect('talim:bosh_sahifa')
    return render(request, 'landing.html')

@login_required(login_url='/hisoblar/login/')
def bosh_sahifa_view(request):
    """Foydalanuvchi tizimga kirgan zahoti roliga qarab yo'naltiriladi"""
    user = request.user
    
    if user.rol == 'oqituvchi':
        return redirect('talim:oqituvchi_dashboard')
    elif user.rol == 'oquvchi':
        return redirect('talim:oquvchi_profil')
    elif user.rol == 'ota_ona':
        return redirect('talim:ota_ona_view')
    elif user.rol == 'admin' or user.is_superuser:
        return redirect('/admin/')
    
    # Roli aniqlanmagan bo'lsa
    return render(request, 'base.html')


# -------------------------------------------------------------------------
# 2. O'QITUVCHI BO'LIMI (DASHBOARD VA JURNAL)
# -------------------------------------------------------------------------

@login_required
def oqituvchi_dashboard_view(request):
    """O'qituvchi o'ziga biriktirilgan barcha darslarni (Sinf + Fan) ko'radi"""
    if request.user.rol != 'oqituvchi':
        return redirect('talim:bosh_sahifa')

    # O'qituvchining 'Taqsimot'lari (Jadval bo'yicha biriktirilgan darslari)
    darslar = Taqsimot.objects.filter(oqituvchi=request.user).select_related('sinf', 'fan')
    
    return render(request, 'oqituvchi/dashboard.html', {'taqsimotlar': darslar})


@login_required
def oqituvchi_jurnal_view(request, taqsimot_id):
    """
    Katakchali jurnal mantiqi. 
    Baho qo'yish, yangi mavzu kiritish va davomat qilish shu yerda hal bo'ladi.
    """
    # Circular Import (Aylana xato) bo'lmasligi uchun funksiya ichida import qilamiz
    from apps.tahlil.views import tahlilni_shakllantirish

    user = request.user
    if user.rol != 'oqituvchi':
        return redirect('talim:bosh_sahifa')

    # 1. Taqsimot (Sinf + Fan) ma'lumotini olamiz
    taqsimot = get_object_or_404(Taqsimot, id=taqsimot_id, oqituvchi=user)
    
    # 2. Sinf o'quvchilari (Ismi bo'yicha saralangan)
    sinf_oquvchilari = Foydalanuvchi.objects.filter(sinf=taqsimot.sinf, rol='oquvchi').order_by('first_name')
    
    # 3. Mavzular (Sana bo'yicha tartiblangan)
    mavzular = Mavzu.objects.filter(taqsimot=taqsimot).order_by('sana')

    # --- MATRIX LOGIC: Baho va Davomatni lug'atlarga yig'amiz (Template-da ishlatish uchun) ---
    for oquvchi in sinf_oquvchilari:
        # Baholar: {mavzu_id: baho_obj}
        oquvchi.tayyor_baholar = {b.mavzu_id: b for b in Baho.objects.filter(oquvchi=oquvchi, mavzu__taqsimot=taqsimot)}
        # Davomat: {mavzu_id: davomat_obj}
        oquvchi.tayyor_davomat = {d.mavzu_id: d for d in Davomat.objects.filter(oquvchi=oquvchi, mavzu__taqsimot=taqsimot)}

    # --- POST SO'ROVLARINI QABUL QILISH (SAQLASH) ---
    if request.method == "POST":
        # A) YANGI DARS MAVZUSI QO'SHISH
        if 'mavzu_nomi' in request.POST:
            mavzu_nomi = request.POST.get('mavzu_nomi')
            dars_sana = request.POST.get('sana')
            try:
                Mavzu.objects.create(taqsimot=taqsimot, mavzu_nomi=mavzu_nomi, sana=dars_sana)
                messages.success(request, "Yangi dars mavzusi jurnalga qo'shildi.")
            except:
                messages.error(request, "Xato: Bu kunda dars mavzusi allaqachon mavjud!")

        # B) O'QUVCHINI BAHOLASH YOKI DAVOMATINI BELGILASH
        elif 'baho_qiymati' in request.POST or 'davomat_holati' in request.POST:
            with transaction.atomic():
                oquvchi_id = request.POST.get('oquvchi_id')
                mavzu_id = request.POST.get('mavzu_id')
                oquvchi_obj = get_object_or_404(Foydalanuvchi, id=oquvchi_id)
                mavzu_obj = get_object_or_404(Mavzu, id=mavzu_id)

                # 1. Baho qo'yish mantiqi
                if request.POST.get('baho_qiymati'):
                    qiymat = request.POST.get('baho_qiymati')
                    izoh = request.POST.get('izoh', '')
                    Baho.objects.update_or_create(
                        oquvchi=oquvchi_obj, mavzu=mavzu_obj,
                        defaults={'qiymati': qiymat, 'izoh': izoh}
                    )
                    # Baho bo'lsa, o'quvchi avtomatik 'Keldi' deb hisoblanadi
                    Davomat.objects.update_or_create(oquvchi=oquvchi_obj, mavzu=mavzu_obj, defaults={'keldi': True})
                    messages.success(request, f"{oquvchi_obj.first_name} baholandi.")
                
                # 2. Davomatni o'zini o'zgartirish (S - Sababsiz qilish)
                if 'davomat_holati' in request.POST:
                    holat = request.POST.get('holat')
                    Davomat.objects.update_or_create(
                        oquvchi=oquvchi_obj, mavzu=mavzu_obj,
                        defaults={'keldi': True if holat == 'keldi' else False}
                    )
                    # Agar kelmagan (S) bo'lsa, mavjud bahosini o'chiramiz
                    if holat == 'kelmadi':
                        Baho.objects.filter(oquvchi=oquvchi_obj, mavzu=mavzu_obj).delete()
                        messages.warning(request, f"{oquvchi_obj.first_name} darsda yo'q (S) deb belgilandi.")

                # O'quvchi umumiy tahlilini (Pulse) darhol yangilaymiz
                tahlilni_shakllantirish(oquvchi_obj)

        return redirect('talim:oqituvchi_jurnal', taqsimot_id=taqsimot.id)

    return render(request, 'oqituvchi/jurnal.html', {
        'taqsimot': taqsimot,
        'oquvchilar': sinf_oquvchilari,
        'mavzular': mavzular,
    })


# -------------------------------------------------------------------------
# 3. O'QUVCHI VA OTA-ONA BO'LIMI (ANALITIKA)
# -------------------------------------------------------------------------

@login_required
def oquvchi_profil_view(request):
    """O'quvchi o'z sinfini, barcha fanlarini, baholarini va tahlilini ko'radi"""
    from apps.tahlil.views import oquvchi_bilimini_tahlil_qilish

    user = request.user
    if user.rol != 'oquvchi':
        return redirect('talim:bosh_sahifa')

    # O'quvchi o'qiydigan sinfdagi fanlar ro'yxati
    darslar = Taqsimot.objects.filter(sinf=user.sinf).select_related('fan', 'oqituvchi')
    # Bilim tahlili (Analitika algoritmi)
    tahlil = oquvchi_bilimini_tahlil_qilish(user.id)
    # Baholar tarixi
    baholar = user.baholari.all().select_related('mavzu__taqsimot__fan').order_by('-mavzu__sana')

    return render(request, 'oquvchi/profil.html', {
        'darslar': darslar,
        'tahlil': tahlil,
        'baholar': baholar,
        'sinf': user.sinf
    })

@login_required
def ota_ona_view(request):
    """Ota-onalar o'z farzandining bilim darajasini kuzatadigan sahifa"""
    from apps.tahlil.views import oquvchi_bilimini_tahlil_qilish

    user = request.user
    if user.rol != 'ota_ona' or not user.farzandi:
        messages.warning(request, "Sizga hali farzand biriktirilmagan.")
        return redirect('talim:bosh_sahifa')

    farzand = user.farzandi
    # Farzand tahlili va baholari
    tahlil = oquvchi_bilimini_tahlil_qilish(farzand.id)
    baholar = farzand.baholari.all().select_related('mavzu__taqsimot__fan').order_by('-mavzu__sana')
    davomatlar = farzand.davomati.all().order_by('-mavzu__sana')

    return render(request, 'ota_ona/farzand.html', {
        'farzand': farzand,
        'tahlil': tahlil,
        'baholar': baholar,
        'davomatlar': davomatlar
    })