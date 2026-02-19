/**
 * 'BilimNazoratchi' tizimining asosiy interaktiv logikasi (JavaScript).
 * 
 * Vazifasi:
 * 1. Bildirishnomalarni (Alerts) boshqarish.
 * 2. Sahifa elementlari yuklanishini nazorat qilish.
 * 3. Foydalanuvchi interfeysini interaktiv qilish.
 */

// Sahifa tarkibi (DOM) to'liq yuklangandan so'ng kodni ishga tushiramiz
document.addEventListener('DOMContentLoaded', function() {

    // Tizim holatini tekshirish uchun konsolga professional xabar chiqaramiz
    console.log("BilimNazoratchi tizimi muvaffaqiyatli yuklandi!");

    /**
     * 1. BILD IRISHNOMALARNI (ALERTS) AVTOMATIK YOPISH
     * Django orqali yuborilgan muvaffaqiyat yoki xatolik xabarlari (Django messages) 
     * foydalanuvchiga xalaqit bermasligi uchun 5 soniyadan so'ng yopiladi.
     */
    function bildirishnomalarniAvtomatikTozalash() {
        // Sahifadagi barcha alert elementlarini qidirib topamiz
        const xabarlar = document.querySelectorAll('.alert');

        // Har bir topilgan xabarni vaqt bo'yicha yopamiz
        xabarlar.forEach(function(xabar) {
            // Bootstrap Alert API mavjudligini tekshiramiz
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                setTimeout(function() {
                    try {
                        // Bootstrap Alert ob'ektini olamiz va uni yopamiz
                        const bsAlert = bootstrap.Alert.getOrCreateInstance(xabar);
                        if (bsAlert) {
                            bsAlert.close();
                            console.log("Xabarnoma muddati tugadi va yopildi.");
                        }
                    } catch (xato) {
                        // Agar kutilmagan xato bo'lsa, shunchaki elementni yashiramiz
                        xabar.style.display = 'none';
                    }
                }, 5000); // 5000 ms = 5 soniya
            }
        });
    }

    // Funksiyani ishga tushiramiz
    bildirishnomalarniAvtomatikTozalash();

    /**
     * 2. MODALLARNI NAZORAT QILISH (Ixtiyoriy)
     * Baho qo'yish oynasi ochilganda yoki yopilganda biror amal 
     * bajarish kerak bo'lsa, shu yerda yoziladi.
     */
    const bahoModallari = document.querySelectorAll('.modal');
    bahoModallari.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function () {
            // Modal yopilganda formani tozalash mantiqi (kerak bo'lsa)
            console.log("Baholash oynasi yopildi.");
        });
    });

});