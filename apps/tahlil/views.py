"""
'BilimNazoratchi' Loyihasi - Analitika va Matematik Hisob-kitoblar Markazi.

Vazifasi:
1. O'quvchilarning baholarini tahlil qilib, o'rtacha ko'rsatkichlarni hisoblash.
2. Bilim dinamikasini (Trend) aniqlash.
3. Maktab ma'muriyati uchun umumiy statistik hisobotlarni shakllantirish.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.talim.models import Baho
from .models import OquvchiTahlili

# -------------------------------------------------------------------------
# 1. TAHLILNI HISOBLASH VA YANGILASH ALGORITMI (O'qituvchi baho qo'yganda)
# -------------------------------------------------------------------------
def tahlilni_shakllantirish(oquvchi):
    """
    Ushbu funksiya o'quvchi baho olgan zahoti ishga tushadi.
    Vazifasi: GPA hisoblash, trendni aniqlash va bazadagi 'OquvchiTahlili'ni yangilash.
    """
    # # IZOH: O'quvchining barcha baholarini sana bo'yicha tartiblab olamiz.
    baholar_qs = Baho.objects.filter(oquvchi=oquvchi).order_by('mavzu__sana')
    
    if not baholar_qs.exists():
        return None

    # A) O'rtacha ballni hisoblash
    ballar_ruyxati = [b.qiymati for b in baholar_qs]
    ortacha = sum(ballar_ruyxati) / len(ballar_ruyxati)

    # B) Trendni aniqlash (Oxirgi 3 baho tahlili)
    trend_holati = 'barqaror'
    if len(ballar_ruyxati) >= 3:
        oxirgi_uchta_ortacha = sum(ballar_ruyxati[-3:]) / 3
        oldingi_ballar = ballar_ruyxati[:-3]
        if oldingi_ballar:
            oldingi_ortacha = sum(oldingi_ballar) / len(oldingi_ballar)
            if oxirgi_uchta_ortacha > oldingi_ortacha:
                trend_holati = 'osish'
            elif oxirgi_uchta_ortacha < oldingi_ortacha:
                trend_holati = 'pasayish'
    
    # D) Xavf darajasini belgilash
    xavf_ostida = True if ortacha < 3.5 else False

    # E) Bazaga saqlash
    tahlil_obj, yaratildi = OquvchiTahlili.objects.get_or_create(oquvchi=oquvchi)
    tahlil_obj.ortacha_ball = round(ortacha, 2)
    tahlil_obj.trend = trend_holati
    tahlil_obj.xavf_ostida = xavf_ostida
    tahlil_obj.save()
    
    return tahlil_obj


# -------------------------------------------------------------------------
# 2. BAZADAGI TAHLILNI OLIB BERISH (Profil va Dashboardlar uchun)
# -------------------------------------------------------------------------
def oquvchi_bilimini_tahlil_qilish(oquvchi_id):
    """
    BU FUNKSIYA IMPORT XATOSINI YO'QOTADI.
    Vazifasi: O'quvchi ID raqami orqali uning tayyor tahlil natijasini lug'atda qaytarish.
    """
    try:
        tahlil_obj = OquvchiTahlili.objects.get(oquvchi_id=oquvchi_id)
        
        # Trend va ranglarni xaritaga solamiz
        trend_izohi = {'osish': "O'sish", 'pasayish': "Pasayish", 'barqaror': "Barqaror"}
        trend_belgilari = {'osish': '⬆', 'pasayish': '⬇', 'barqaror': '➡'}
        
        return {
            "ortacha": tahlil_obj.ortacha_ball,
            "holat": "Xavf ostida" if tahlil_obj.xavf_ostida else "Yaxshi",
            "rang": "danger" if tahlil_obj.xavf_ostida else "success",
            "trend": trend_izohi.get(tahlil_obj.trend, "Barqaror"),
            "trend_belgi": trend_belgilari.get(tahlil_obj.trend, "➡")
        }
    except OquvchiTahlili.DoesNotExist:
        # Agar hali tahlil hisoblanmagan bo'lsa
        return {
            "ortacha": 0.0, "holat": "Noma'lum", "rang": "secondary", 
            "trend": "Neytral", "trend_belgi": "➖"
        }


# -------------------------------------------------------------------------
# 3. UMUMIY STATISTIKA SAHIFASI (O'qituvchilar va Admin uchun)
# -------------------------------------------------------------------------
@login_required
def statistika_markazi_view(request):
    """
    Maktabdagi barcha o'quvchilarning tahliliy jadvalini ko'rsatuvchi sahifa.
    """
    foydalanuvchi = request.user

    if foydalanuvchi.rol not in ['admin', 'oqituvchi']:
        messages.error(request, "Sizda ushbu ma'lumotlarni ko'rish huquqi yo'q!")
        return redirect('talim:bosh_sahifa')

    tahlillar = OquvchiTahlili.objects.select_related('oquvchi', 'oquvchi__sinf').all().order_by('ortacha_ball')
    
    jami_oquvchi = tahlillar.count()
    xavf_soni = tahlillar.filter(xavf_ostida=True).count()
    
    muvaffaqiyat_foizi = 0
    if jami_oquvchi > 0:
        muvaffaqiyat_foizi = ((jami_oquvchi - xavf_soni) / jami_oquvchi) * 100

    kontekst = {
        'tahlillar': tahlillar,
        'jami_oquvchi': jami_oquvchi,
        'xavf_soni': xavf_soni,
        'muvaffaqiyat_foizi': round(muvaffaqiyat_foizi, 1),
    }
    
    return render(request, 'tahlil/umumiy_statistika.html', kontekst)
