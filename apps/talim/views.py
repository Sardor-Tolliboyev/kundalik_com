"""
'BilimNazoratchi' Loyihasi - Ta'lim Jarayoni Mantiqiy Markazi (Views).

Vazifasi:
1. Foydalanuvchini roliga qarab tegishli sahifaga yo'naltirish.
2. O'qituvchi uchun darslar ro'yxati va elektron jurnalni (Matrix) shakllantirish.
3. Baholash va Davomatni (yo'qlama) saqlash mantiqini boshqarish.
4. O'quvchi va ota-onalar uchun tahliliy ma'lumotlarni yig'ish.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import date

# Loyihamiz modellarini va tahlil mantiqini import qilamiz
from .models import Sinf, Fan, Taqsimot, Mavzu, Baho, Davomat
from apps.hisoblar.models import Foydalanuvchi
from apps.tahlil.views import tahlilni_shakllantirish, oquvchi_bilimini_tahlil_qilish

# -------------------------------------------------------------------------
# 1. ASOSIY YO'NALTIRUVCHI (HOME REDIRECTOR)
# -------------------------------------------------------------------------
@login_required
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
    
    return render(request, 'base.html')


# -------------------------------------------------------------------------
# 2. O'QITUVCHI ISH STOLI (DASHBOARD)
# -------------------------------------------------------------------------
@login_required
def oqituvchi_dashboard_view(request):
    """O'qituvchi o'ziga biriktirilgan darslarni (Sinf + Fan) ko'radi"""
    if request.user.rol != 'oqituvchi':
        return redirect('talim:bosh_sahifa')

    # O'qituvchiga 'Taqsimot' orqali biriktirilgan darslarni bazadan olamiz
    darslar = Taqsimot.objects.filter(oqituvchi=request.user).select_related('sinf', 'fan')

    return render(request, 'oqituvchi/dashboard.html', {'taqsimotlar': darslar})


# -------------------------------------------------------------------------
# 3. ELEKTRON JURNAL (Matrix View: Baholash va Davomat)
# -------------------------------------------------------------------------
@login_required
def oqituvchi_jurnal_view(request, taqsimot_id):
    """
    Katakchali jurnal ko'rinishi. 
    Vazifasi: Ma'lumotlarni jadval ko'rinishida yig'ish, baho va davomatni saqlash.
    """
    user = request.user
    if user.rol != 'oqituvchi':
        return redirect('talim:bosh_sahifa')

    # 1. Taqsimot (Sinf + Fan) ma'lumotini olamiz
    taqsimot = get_object_or_404(Taqsimot, id=taqsimot_id, oqituvchi=user)
    # 2. Shu sinfdagi barcha o'quvchilarni olamiz
    sinf_oquvchilari = Foydalanuvchi.objects.filter(sinf=taqsimot.sinf, rol='oquvchi').order_by('first_name')
    # 3. Shu darsga oid kiritilgan barcha mavzularni (kunlarni) olamiz
    mavzular = Mavzu.objects.filter(taqsimot=taqsimot).order_by('sana')

    # --- PROFESSIONAL MANTIQ: Baho va Davomatni Matrix (Lug'at) ko'rinishida yig'ish ---
    for oquvchi in sinf_oquvchilari:
        # Baholar lug'ati: {mavzu_id: baho_obyekti}
        baho_lugati = {}
        for b in Baho.objects.filter(oquvchi=oquvchi, mavzu__taqsimot=taqsimot):
            baho_lugati[b.mavzu_id] = b
        oquvchi.tayyor_baholar = baho_lugati

        # Davomat lug'ati: {mavzu_id: davomat_obyekti}
        davomat_lugati = {}
        for d in Davomat.objects.filter(oquvchi=oquvchi, mavzu__taqsimot=taqsimot):
            davomat_lugati[d.mavzu_id] = d
        oquvchi.tayyor_davomat = davomat_lugati

    # --- MA'LUMOTLARNI SAQLASH (POST SO'ROVLARI) ---
    if request.method == "POST":
        
        # A) YANGI DARS MAVZUSINI KIRITISH
        if 'mavzu_nomi' in request.POST:
            mavzu_nomi = request.POST.get('mavzu_nomi')
            dars_sana = request.POST.get('sana')
            try:
                Mavzu.objects.create(taqsimot=taqsimot, mavzu_nomi=mavzu_nomi, sana=dars_sana)
                messages.success(request, "Yangi dars kuni jurnalga qo'shildi.")
            except:
                messages.error(request, "Xato: Bu kunda dars mavzusi allaqachon mavjud!")

        # B) O'QUVCHINI BAHOLASH YOKI DAVOMAT QILISH
        elif 'baho_qiymati' in request.POST or 'davomat_holati' in request.POST:
            with transaction.atomic():
                oquvchi_id = request.POST.get('oquvchi_id')
                mavzu_id = request.POST.get('mavzu_id')
                
                oquvchi_obj = get_object_or_404(Foydalanuvchi, id=oquvchi_id)
                mavzu_obj = get_object_or_404(Mavzu, id=mavzu_id)

                # 1. Agar baho kiritilgan bo'lsa
                if 'baho_qiymati' in request.POST and request.POST.get('baho_qiymati'):
                    qiymat = request.POST.get('baho_qiymati')
                    izoh = request.POST.get('izoh', '')
                    Baho.objects.update_or_create(
                        oquvchi=oquvchi_obj, mavzu=mavzu_obj,
                        defaults={'qiymati': qiymat, 'izoh': izoh}
                    )
                    # Baho qo'yilganda o'quvchi avtomatik 'Keldi' deb hisoblanadi
                    Davomat.objects.update_or_create(
                        oquvchi=oquvchi_obj, mavzu=mavzu_obj,
                        defaults={'keldi': True}
                    )
                    messages.success(request, f"{oquvchi_obj.first_name} uchun baho saqlandi.")

                # 2. Agar davomat holati kiritilgan bo'lsa (Siz so'ragan qism)
                if 'davomat_holati' in request.POST:
                    holat = request.POST.get('holat') # 'keldi' yoki 'kelmadi'
                    
                    # Davomatni yozamiz yoki yangilaymiz
                    Davomat.objects.update_or_create(
                        oquvchi=oquvchi_obj, mavzu=mavzu_obj,
                        defaults={'keldi': True if holat == 'keldi' else False}
                    )
                    
                    # Agar o'quvchi kelmagan deb belgilansa, mavjud bahosini o'chirib tashlaymiz
                    if holat == 'kelmadi':
                        Baho.objects.filter(oquvchi=oquvchi_obj, mavzu=mavzu_obj).delete()
                        messages.warning(request, f"{oquvchi_obj.first_name} darsda ishtirok etmadi (S).")
                    else:
                        messages.info(request, f"{oquvchi_obj.first_name} darsda ishtirok etdi.")

                # 5-talaba algoritmini ishga tushirib, tahlilni darhol yangilaymiz
                tahlilni_shakllantirish(oquvchi_obj)

        return redirect('talim:jurnal', taqsimot_id=taqsimot.id)

    return render(request, 'oqituvchi/jurnal.html', {
        'taqsimot': taqsimot,
        'oquvchilar': sinf_oquvchilari,
        'mavzular': mavzular,
    })


# -------------------------------------------------------------------------
# 4. O'QUVCHI SHAXSIY PROFILI (PROFILE VIEW)
# -------------------------------------------------------------------------
@login_required
def oquvchi_profil_view(request):
    """O'quvchi o'zining barcha fanlari, baholari va bilim grafigini ko'radi"""
    user = request.user
    if user.rol != 'oquvchi':
        return redirect('talim:bosh_sahifa')

    # O'quvchi sinfidagi barcha fanlarni 'Taqsimot' orqali topamiz
    sinf_darslari = Taqsimot.objects.filter(sinf=user.sinf).select_related('fan', 'oqituvchi')
    
    # 5-talaba algoritmi yordamida tahlillarni olamiz
    tahlil = oquvchi_bilimini_tahlil_qilish(user.id)
    
    # Barcha baholar tarixi
    baholar = user.baholari.all().select_related('mavzu__taqsimot__fan').order_by('-mavzu__sana')

    return render(request, 'oquvchi/profil.html', {
        'darslar': sinf_darslari,
        'tahlil': tahlil,
        'baholar': baholar,
        'sinf': user.sinf
    })


# -------------------------------------------------------------------------
# 5. OTA-ONA NAZORATI (CHILD TRACKING)
# -------------------------------------------------------------------------
@login_required
def ota_ona_view(request):
    """Ota-onalar farzandining bilim darajasini kuzatadigan sahifa"""
    user = request.user
    if user.rol != 'ota_ona' or not user.farzandi:
        messages.warning(request, "Sizga hali farzand biriktirilmagan.")
        return redirect('talim:bosh_sahifa')

    farzand = user.farzandi
    # Farzand tahlili, baholari va davomati
    tahlil = oquvchi_bilimini_tahlil_qilish(farzand.id)
    baholar = farzand.baholari.all().select_related('mavzu__taqsimot__fan').order_by('-mavzu__sana')
    davomatlar = farzand.davomati.all().order_by('-mavzu__sana')

    return render(request, 'ota_ona/farzand.html', {
        'farzand': farzand,
        'tahlil': tahlil,
        'baholar': baholar,
        'davomatlar': davomatlar
    })