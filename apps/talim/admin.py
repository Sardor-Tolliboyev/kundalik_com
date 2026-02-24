"""
'BilimNazoratchi' Loyihasi - Ta'lim Jarayoni Admin Sozlamalari.

Vazifasi:
1. Sinf, Fan, Taqsimot va Baholarni admin panelda boshqarish.
2. O'quvchilar ro'yxatini Exceldan ommaviy yuklash (Import).
3. Yuklangan o'quvchilar uchun Login va Parollarni Excel formatida qaytarish (Export).
"""

import pandas as pd
import io
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse
from django.db import transaction

# Modellarimizni import qilamiz
from .models import Sinf, Fan, Taqsimot, Mavzu, Baho, Davomat
from apps.hisoblar.models import Foydalanuvchi

# -------------------------------------------------------------------------
# 1. SINF ADMINI: Excel yuklash funksiyasi bilan
# -------------------------------------------------------------------------
@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    """
    Sinflarni boshqarish va o'quvchilarni ommaviy integratsiya qilish paneli.
    """
    list_display = ('nomi', 'o_quvchilar_soni')
    search_fields = ('nomi',)
    
    # Excel tugmasi ko'rinishi uchun shablonni ulaymiz
    change_list_template = "admin/talim/sinf/change_list.html"

    @admin.display(description="O'quvchilar soni")
    def o_quvchilar_soni(self, obj):
        """Sinfdagi jami o'quvchilar sonini hisoblab ko'rsatadi"""
        return obj.sinfdagi_oquvchilar.count()

    # --- MAXSUS URL'LAR (EXCEL INTEGRATSIYASI UCHUN) ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('excel-yuklash/', self.admin_site.admin_view(self.excel_yuklash_view), name='talim_sinf_excel_yuklash'),
        ]
        return custom_urls + urls

    # --- EXCEL IMPORT VA AVTOMATIK EXPORT MANTIQI ---
    def excel_yuklash_view(self, request):
        """
        Excel faylni o'qib, o'quvchilarni yaratadi va 
        ulardan iborat login-parol ro'yxatini qaytaradi.
        """
        if request.method == "POST":
            file = request.FILES.get('excel_fayl')
            sinf_id = request.POST.get('sinf_id')
            
            if not file or not sinf_id:
                messages.error(request, "Fayl yoki sinf tanlanmadi!")
                return redirect(".")
            
            try:
                # 1. Excelni Pandas yordamida o'qiymiz
                df = pd.read_excel(file)
                sinf_obj = Sinf.objects.get(id=sinf_id)
                
                yaratilgan_o_quvchilar = []
                standart_parol = "12345678" # Tizim o'rnatadigan boshlang'ich parol

                # Ma'lumotlarni bazaga yozishni bitta tranzaksiyaga olamiz (Xavfsizlik uchun)
                with transaction.atomic():
                    for _, row in df.iterrows():
                        # Excel ustun nomi rasmga ko'ra: 'Ism familiyasi'
                        fio = str(row['Ism familiyasi']).strip()
                        
                        # Ismdan professional login yasaymiz (kichik harf, probelsiz)
                        login = fio.replace(" ", "_").lower()[:20]
                        
                        # Foydalanuvchini bazada yaratamiz
                        user, created = Foydalanuvchi.objects.get_or_create(
                            username=login,
                            defaults={
                                'first_name': fio,
                                'rol': 'oquvchi',
                                'sinf': sinf_obj
                            }
                        )
                        
                        # Agar foydalanuvchi yangi bo'lsa, parol o'rnatamiz
                        if created:
                            user.set_password(standart_parol)
                            user.save()
                        
                        # Hisobot fayli uchun ma'lumot yig'amiz
                        yaratilgan_o_quvchilar.append({
                            'F.I.SH': fio,
                            'Login (Username)': login,
                            'Parol': standart_parol,
                            'Sinfi': sinf_obj.nomi
                        })

                # 2. LOGIN-PAROLLAR RO'YXATINI EXCELDA GENERATSIYA QILISH
                res_df = pd.DataFrame(yaratilgan_o_quvchilar)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_df.to_excel(writer, index=False, sheet_name='Oquvchi_Loginlari')
                
                output.seek(0)

                # 3. GENERATSIYA BO'LGAN FAYLNI BRAUZERGA YUKLASH UCHUN YUBORAMIZ
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="Yangi_Loginlar_{sinf_obj.nomi}.xlsx"'
                
                # Muvaffaqiyat xabari (Redirect bo'lmagani uchun keyingi kirishda chiqadi)
                messages.success(request, f"{len(yaratilgan_o_quvchilar)} ta o'quvchi bazaga qo'shildi va loginlar fayli tayyorlandi.")
                
                return response

            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
                return redirect(".")
        
        # Sahifani ko'rsatish
        return render(request, "admin/excel_import.html", {"sinflar": Sinf.objects.all()})


# -------------------------------------------------------------------------
# 2. BOSHQA MODELLAR ADMIN SOZLAMALARI
# -------------------------------------------------------------------------

@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)

@admin.register(Taqsimot)
class TaqsimotAdmin(admin.ModelAdmin):
    """Qaysi o'qituvchi qaysi sinfga dars o'tishini boshqarish"""
    list_display = ('sinf', 'fan', 'oqituvchi', 'kun', 'soat')
    list_filter = ('sinf', 'fan', 'oqituvchi', 'kun')
    search_fields = ('oqituvchi__first_name', 'sinf__nomi')

@admin.register(Mavzu)
class MavzuAdmin(admin.ModelAdmin):
    """Kundalik dars mavzulari monitoringi"""
    list_display = ('sana', 'taqsimot', 'mavzu_nomi')
    list_filter = ('sana', 'taqsimot__sinf', 'taqsimot__fan')
    date_hierarchy = 'sana' # Vaqt bo'yicha qulay navigatsiya

@admin.register(Baho)
class BahoAdmin(admin.ModelAdmin):
    """O'quvchilarning baholarini nazorat qilish"""
    list_display = ('oquvchi', 'fan_nomi', 'qiymati', 'sana_korish')
    list_filter = ('qiymati', 'mavzu__taqsimot__fan')
    search_fields = ('oquvchi__first_name', 'oquvchi__username')

    @admin.display(description="Fan")
    def fan_nomi(self, obj):
        return obj.mavzu.taqsimot.fan.nomi

    @admin.display(description="Sana")
    def sana_korish(self, obj):
        return obj.mavzu.sana

@admin.register(Davomat)
class DavomatAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'mavzu', 'keldi_vizual')
    list_filter = ('keldi', 'mavzu__sana')

    @admin.display(description="Ishtirok")
    def keldi_vizual(self, obj):
        return "✅ Keldi" if obj.keldi else "❌ Kelmadi"