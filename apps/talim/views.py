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
from datetime import date, timedelta

from django.utils.dateparse import parse_date
from django.db import IntegrityError
from datetime import datetime

# Loyihamiz modellarini va tahlil mantiqini import qilamiz
from .models import Sinf, Fan, Taqsimot, Mavzu, Baho, Davomat
from apps.hisoblar.models import Foydalanuvchi
from apps.tahlil.views import tahlilni_shakllantirish, oquvchi_bilimini_tahlil_qilish
def landing_view(request):
    """
    Tizimning birinchi yuzi. 
    Hamma uchun landing.html ni ko'rsatadi.
    (Dashboardga o'tish tugmasi shablonda `user.is_authenticated` orqali chiqariladi.)
    """
    return render(request, 'landing.html')


def _hafta_boshi(topilgan_sana: date) -> date:
    """
    Berilgan sananing haftadagi dushanbasini qaytaradi.

    # IZOH: Python'da `weekday()` -> dushanba=0 ... yakshanba=6
    """
    return topilgan_sana - timedelta(days=topilgan_sana.weekday())


def _dars_slotlari_yaratish():
    """
    Standart dars vaqtlarini yaratadi (1-smena + 2-smena).

    Talab:
    - 45 daqiqa dars
    - 5 daqiqa tanaffus
    - 1-smena: 08:00 dan 6 ta dars
    - 2-smena: 13:00 dan 6 ta dars

    Qaytadi: [{"dars_raqami": 1..6, "smena": "1"|"2", "start_str": "08:00", "end_str": "08:45", "range_str": "08:00 - 08:45"}]
    """
    # # IZOH: Maktab jadvali standarti (o'zgartirmasdan turib tushunarli qildik)
    dars_daqiqa = 45
    tanaffus_daqiqa = 5
    har_smenadagi_dars_soni = 6

    def slotlar_yasash(smena_boshlanishi_hhmm: str, smena: str):
        boshlanish_vaqti = datetime.strptime(smena_boshlanishi_hhmm, "%H:%M")
        slotlar: list[dict] = []
        joriy_vaqt = boshlanish_vaqti
        for dars_index in range(har_smenadagi_dars_soni):
            tugash_vaqti = joriy_vaqt + timedelta(minutes=dars_daqiqa)
            slotlar.append(
                {
                    "dars_raqami": dars_index + 1,
                    "smena": smena,
                    "start_str": joriy_vaqt.strftime("%H:%M"),
                    "end_str": tugash_vaqti.strftime("%H:%M"),
                    "range_str": f"{joriy_vaqt.strftime('%H:%M')} - {tugash_vaqti.strftime('%H:%M')}",
                }
            )
            joriy_vaqt = tugash_vaqti + timedelta(minutes=tanaffus_daqiqa)
        return slotlar

    return slotlar_yasash("08:00", "1") + slotlar_yasash("13:00", "2")


def _slotlar_bilan_birlash(taqsimotlar, *, smena: str):
    """
    Standart slotlar + bazada bor bo'lgan (no-standart) vaqtlarni birlashtiradi.

    # IZOH: Agar bazada 08:05 kabi no-standart vaqt bo'lsa, u ham ko'rinib qoladi.
    """
    barcha_slotlar = _dars_slotlari_yaratish()

    if smena == "1":
        slotlar = [s for s in barcha_slotlar if s["smena"] == "1"]
    elif smena == "2":
        slotlar = [s for s in barcha_slotlar if s["smena"] == "2"]
    else:
        slotlar = barcha_slotlar

    mavjud_vaqtlar = {s["start_str"] for s in slotlar}

    # No-standart slotlar (end = start + 45 min deb olamiz)
    for taqsimot in taqsimotlar:
        start_str = taqsimot.soat.strftime("%H:%M")
        # # IZOH: smena tanlangan bo'lsa, vaqt bo'yicha mos kelmaydiganlarini tashlab yuboramiz.
        if smena in {"1", "2"}:
            if (smena == "1" and start_str >= "13:00") or (smena == "2" and start_str < "13:00"):
                continue
        if start_str in mavjud_vaqtlar:
            continue
        start_dt = datetime.strptime(start_str, "%H:%M")
        end_dt = start_dt + timedelta(minutes=45)
        smena_val = "1" if start_str < "13:00" else "2"
        slotlar.append(
            {
                "dars_raqami": None,
                "smena": smena_val,
                "start_str": start_str,
                "end_str": end_dt.strftime("%H:%M"),
                "range_str": f"{start_str} - {end_dt.strftime('%H:%M')}",
            }
        )
        mavjud_vaqtlar.add(start_str)

    # Tartiblash
    slotlar.sort(key=lambda s: s["start_str"])
    return slotlar


def _taqsimot_queryset_user_uchun(request_user, *, sinf_id: str | None, oqituvchi_id: str | None):
    """
    Haftalik dars jadvali uchun kerakli Taqsimot queryset'ini roldan kelib chiqib tayyorlaydi.

    # IZOH: admin (yoki is_staff) uchun filtrlar query param orqali keladi.
    """
    foydalanuvchi = request_user

    # A) O'qituvchi: faqat o'z darslari
    if getattr(foydalanuvchi, "rol", "") == "oqituvchi":
        return (
            Taqsimot.objects.filter(oqituvchi=foydalanuvchi)
            .select_related("sinf", "fan", "oqituvchi")
            .order_by("kun", "soat")
        )

    # B) O'quvchi: sinfidagi barcha darslar
    if getattr(foydalanuvchi, "rol", "") == "oquvchi":
        if not foydalanuvchi.sinf_id:
            return Taqsimot.objects.none()
        return (
            Taqsimot.objects.filter(sinf_id=foydalanuvchi.sinf_id)
            .select_related("sinf", "fan", "oqituvchi")
            .order_by("kun", "soat")
        )

    # C) Ota-ona: farzandining sinfidagi darslar
    if getattr(foydalanuvchi, "rol", "") == "ota_ona":
        if not getattr(foydalanuvchi, "farzandi_id", None):
            return Taqsimot.objects.none()
        farzand = Foydalanuvchi.objects.filter(id=foydalanuvchi.farzandi_id).only("id", "sinf_id").first()
        if not farzand or not farzand.sinf_id:
            return Taqsimot.objects.none()
        return (
            Taqsimot.objects.filter(sinf_id=farzand.sinf_id)
            .select_related("sinf", "fan", "oqituvchi")
            .order_by("kun", "soat")
        )

    # D) Admin / xodim: filtr bo'yicha ko'rsatamiz (katta bazada haddan tashqari yuk bo'lmasin)
    if foydalanuvchi.is_staff or getattr(foydalanuvchi, "rol", "") == "admin":
        taqsimot_qs = Taqsimot.objects.all().select_related("sinf", "fan", "oqituvchi").order_by("kun", "soat")
        if sinf_id:
            taqsimot_qs = taqsimot_qs.filter(sinf_id=sinf_id)
        if oqituvchi_id:
            taqsimot_qs = taqsimot_qs.filter(oqituvchi_id=oqituvchi_id)
        # Filtrsizlikda bo'sh ko'rsatamiz (foydalanuvchi sinf/o'qituvchi tanlasin)
        if not sinf_id and not oqituvchi_id:
            return Taqsimot.objects.none()
        return taqsimot_qs

    return Taqsimot.objects.none()

# 2. YO'NALTIRUVCHI VIEW (Faqat profilga 'sakrash' uchun)
@login_required(login_url='/hisoblar/login/')
def bosh_sahifa_view(request):
    foydalanuvchi = request.user
    if foydalanuvchi.rol == 'oqituvchi':
        return redirect('talim:oqituvchi_dashboard')
    elif foydalanuvchi.rol == 'oquvchi':
        return redirect('talim:oquvchi_profil')
    elif foydalanuvchi.rol == 'ota_ona':
        return redirect('talim:ota_ona_view')
    return redirect('/admin/')


# -------------------------------------------------------------------------
# 2.5 HAFTALIK DARS JADVALI (BARCHA ROLLAR UCHUN)
# -------------------------------------------------------------------------
@login_required
def haftalik_dars_jadvali_view(request):
    """
    eMaktab uslubiga yaqin haftalik dars jadvali.

    Ko'rish qoidalari:
    - O'qituvchi: o'z darslari
    - O'quvchi: sinfi bo'yicha
    - Ota-ona: farzandi sinfi bo'yicha
    - Admin/xodim: sinf yoki o'qituvchi filtri bilan
    """
    foydalanuvchi = request.user

    # 0) Admin jadvalning o'zidan dars qo'shish/tahrirlash (faqat staff)
    if request.method == "POST":
        if not foydalanuvchi.is_staff and getattr(foydalanuvchi, "rol", "") != "admin":
            messages.error(request, "Sizda dars jadvalini tahrirlash huquqi yo'q.")
            return redirect("talim:haftalik_dars_jadvali")

        taqsimot_id = request.POST.get("taqsimot_id") or None
        sinf_id = request.POST.get("sinf_id")
        oqituvchi_id = request.POST.get("oqituvchi_id")
        fan_id = request.POST.get("fan_id")
        kun = request.POST.get("kun")
        soat_str = request.POST.get("soat")

        if not (sinf_id and oqituvchi_id and fan_id and kun and soat_str):
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring.")
            return redirect(request.get_full_path())

        try:
            soat_value = datetime.strptime(soat_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Vaqt formati noto'g'ri. Namuna: 08:30")
            return redirect(request.get_full_path())

        # # IZOH: Jadvalda 45/5 standart slotlar ishlatiladi. Admin tasodifan boshqa vaqt kiritsa,
        # ekranda "no-standart" bo'lib ham ko'rinadi, lekin baribir formatni bir xil ushlab turamiz.

        # # IZOH: Model constraint: (sinf, kun, soat) unique.
        try:
            if taqsimot_id:
                taqsimot_obj = get_object_or_404(Taqsimot, id=taqsimot_id)
                taqsimot_obj.sinf_id = sinf_id
                taqsimot_obj.oqituvchi_id = oqituvchi_id
                taqsimot_obj.fan_id = fan_id
                taqsimot_obj.kun = kun
                taqsimot_obj.soat = soat_value
                taqsimot_obj.save()
                messages.success(request, "Dars jadvali muvaffaqiyatli yangilandi.")
            else:
                Taqsimot.objects.create(
                    sinf_id=sinf_id,
                    oqituvchi_id=oqituvchi_id,
                    fan_id=fan_id,
                    kun=kun,
                    soat=soat_value,
                )
                messages.success(request, "Yangi dars jadvalga qo'shildi.")
        except IntegrityError:
            messages.error(request, "Xato: Bu sinfda ushbu kun/vaqtda boshqa dars allaqachon mavjud!")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")

        # Post'dan keyin o'sha haftada qolish uchun start paramni saqlab redirect qilamiz
        redirect_url = request.POST.get("redirect_to") or request.get_full_path()

        # # IZOH: Admin filtrsiz sahifada qolib ketmasligi uchun, agar redirect URL'da filtr bo'lmasa,
        # kiritilgan sinf bo'yicha avtomatik filtr qo'shib yuboramiz.
        if (foydalanuvchi.is_staff or getattr(foydalanuvchi, "rol", "") == "admin") and redirect_url:
            if "sinf=" not in redirect_url and "oqituvchi=" not in redirect_url:
                joiner = "&" if "?" in redirect_url else "?"
                redirect_url = f"{redirect_url}{joiner}sinf={sinf_id}"
            if "smena=" not in redirect_url:
                joiner = "&" if "?" in redirect_url else "?"
                redirect_url = f"{redirect_url}{joiner}smena={'1' if soat_str < '13:00' else '2'}"
        return redirect(redirect_url)

    # 1) Haftani aniqlash (query: ?start=YYYY-MM-DD)
    start_param = request.GET.get("start")
    asosiy_sana = parse_date(start_param) if start_param else date.today()
    if not asosiy_sana:
        asosiy_sana = date.today()

    hafta_boshi = _hafta_boshi(asosiy_sana)
    hafta_oxiri = hafta_boshi + timedelta(days=5)  # Dushanba..Shanba (6 kun)

    prev_hafta = hafta_boshi - timedelta(days=7)
    next_hafta = hafta_boshi + timedelta(days=7)

    # 2) Filterlar (ixtiyoriy) + smena
    sinf_id = request.GET.get("sinf")
    oqituvchi_id = request.GET.get("oqituvchi")
    smena = request.GET.get("smena")

    # # IZOH: O'quvchi va ota-ona uchun smena sinfga bog'liq (faqat o'sha smena ko'rsatiladi).
    if getattr(foydalanuvchi, "rol", "") in {"oquvchi", "ota_ona"}:
        if foydalanuvchi.rol == "oquvchi" and getattr(foydalanuvchi, "sinf_id", None):
            sinf_obj = Sinf.objects.filter(id=foydalanuvchi.sinf_id).only("id", "smena").first()
            smena = sinf_obj.smena if sinf_obj else "1"
        elif foydalanuvchi.rol == "ota_ona" and getattr(foydalanuvchi, "farzandi_id", None):
            farzand = (
                Foydalanuvchi.objects.filter(id=foydalanuvchi.farzandi_id)
                .select_related("sinf")
                .only("id", "sinf__smena")
                .first()
            )
            smena = farzand.sinf.smena if farzand and farzand.sinf else "1"
        else:
            smena = "1"
    else:
        if smena not in {"1", "2", "all"}:
            # # IZOH: admin odatda bitta smenani ko'radi; o'qituvchi ham "hammasi" ko'rishi mumkin.
            if foydalanuvchi.is_staff or getattr(foydalanuvchi, "rol", "") == "admin":
                smena = "1"
            else:
                smena = "all"

        # # IZOH: Admin sinfni tanlasa, smena default o'sha sinf smenasiga o'tsin.
        if (foydalanuvchi.is_staff or getattr(foydalanuvchi, "rol", "") == "admin") and sinf_id and request.GET.get("smena") is None:
            sinf_obj = Sinf.objects.filter(id=sinf_id).only("id", "smena").first()
            if sinf_obj:
                smena = sinf_obj.smena

    taqsimotlar = _taqsimot_queryset_user_uchun(foydalanuvchi, sinf_id=sinf_id, oqituvchi_id=oqituvchi_id)

    # 3) Ustunlar (hafta kunlari) va vaqt slotlari
    hafta_kunlari = [
        {"key": "1", "nomi": "Dushanba", "sana": hafta_boshi + timedelta(days=0)},
        {"key": "2", "nomi": "Seshanba", "sana": hafta_boshi + timedelta(days=1)},
        {"key": "3", "nomi": "Chorshanba", "sana": hafta_boshi + timedelta(days=2)},
        {"key": "4", "nomi": "Payshanba", "sana": hafta_boshi + timedelta(days=3)},
        {"key": "5", "nomi": "Juma", "sana": hafta_boshi + timedelta(days=4)},
        {"key": "6", "nomi": "Shanba", "sana": hafta_boshi + timedelta(days=5)},
    ]

    # # IZOH: Default (standart) jadval slotlari + bazada bo'lsa no-standart slotlar
    time_slots = _slotlar_bilan_birlash(taqsimotlar, smena=smena)

    # 4) cell_map[kun][soat] -> [darslar] (o'qituvchida bitta slotda bir nechta sinf bo'lishi mumkin)
    cell_map = {}
    for t in taqsimotlar:
        kun_map = cell_map.setdefault(t.kun, {})
        kun_map.setdefault(t.soat.strftime("%H:%M"), []).append(t)

    # 5) Admin filter ro'yxatlari + modal uchun fanlar
    sinflar = Sinf.objects.all().order_by("nomi")
    oqituvchilar = Foydalanuvchi.objects.filter(rol="oqituvchi").order_by("first_name", "last_name")
    fanlar = Fan.objects.all().order_by("nomi")

    if (foydalanuvchi.is_staff or getattr(foydalanuvchi, "rol", "") == "admin") and not sinf_id and not oqituvchi_id:
        messages.info(request, "Dars jadvalini ko'rish uchun sinf yoki o'qituvchini tanlang.")

    return render(
        request,
        "dars_jadvali/haftalik.html",
        {
            "hafta_boshi": hafta_boshi,
            "hafta_oxiri": hafta_oxiri,
            "prev_hafta": prev_hafta,
            "next_hafta": next_hafta,
            "hafta_kunlari": hafta_kunlari,
            "time_slots": time_slots,
            "cell_map": cell_map,
            "sinflar": sinflar,
            "oqituvchilar": oqituvchilar,
            "fanlar": fanlar,
            "tanlangan_sinf": sinf_id,
            "tanlangan_oqituvchi": oqituvchi_id,
            "tanlangan_smena": smena,
        },
    )
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
    # # IZOH: `request.user` - hozir tizimga kirgan foydalanuvchi
    foydalanuvchi = request.user

    # # IZOH: Admin/xodimlar ham jurnalga kirib baho/davomat qo'ya olishi kerak.
    if foydalanuvchi.rol != 'oqituvchi' and not foydalanuvchi.is_staff:
        return redirect('talim:bosh_sahifa')

    # 1. Taqsimot (Sinf + Fan) ma'lumotini olamiz
    if foydalanuvchi.is_staff and foydalanuvchi.rol != 'oqituvchi':
        taqsimot = get_object_or_404(Taqsimot, id=taqsimot_id)
    else:
        taqsimot = get_object_or_404(Taqsimot, id=taqsimot_id, oqituvchi=foydalanuvchi)
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
    foydalanuvchi = request.user
    if foydalanuvchi.rol != 'oquvchi':
        return redirect('talim:bosh_sahifa')

    # O'quvchi sinfidagi barcha fanlarni 'Taqsimot' orqali topamiz
    sinf_darslari = Taqsimot.objects.filter(sinf=foydalanuvchi.sinf).select_related('fan', 'oqituvchi')
    
    # 5-talaba algoritmi yordamida tahlillarni olamiz
    tahlil = oquvchi_bilimini_tahlil_qilish(foydalanuvchi.id)
    
    # Barcha baholar tarixi
    baholar = foydalanuvchi.baholari.all().select_related('mavzu__taqsimot__fan').order_by('-mavzu__sana')

    return render(request, 'oquvchi/profil.html', {
        'darslar': sinf_darslari,
        'tahlil': tahlil,
        'baholar': baholar,
        'sinf': foydalanuvchi.sinf
    })


# -------------------------------------------------------------------------
# 5. OTA-ONA NAZORATI (CHILD TRACKING)
# -------------------------------------------------------------------------
@login_required
def ota_ona_view(request):
    """Ota-onalar farzandining bilim darajasini kuzatadigan sahifa"""
    foydalanuvchi = request.user
    if foydalanuvchi.rol != 'ota_ona' or not foydalanuvchi.farzandi:
        messages.warning(request, "Sizga hali farzand biriktirilmagan.")
        return redirect('talim:bosh_sahifa')

    farzand = foydalanuvchi.farzandi
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
