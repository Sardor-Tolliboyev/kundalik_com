/**
 * 'BilimNazoratchi' tizimining asosiy interaktiv logikasi (JavaScript).
 * 
 * Vazifasi:
 * 1. Tizim xabarlarini (Alerts) avtomatik yopish.
 * 2. Jadvallar va interaktiv elementlarga dinamik effektlar qo'shish.
 * 3. Formalarni yuborishdan oldin tekshirish (Validation).
 */

// 1. SAHIFA TO'LIQ YUKLANISHINI KUTISH
document.addEventListener('DOMContentLoaded', function() {

    // Tizim holatini dasturchilar konsolida tekshirish
    console.log("BilimNazoratchi tizimi muvaffaqiyatli ishga tushdi!");

    /**
     * 2. BILDIRISHNOMALARNI (ALERTS) AVTOMATIK TOZALASH
     * Django xabarlar tizimi (messages) orqali yuborilgan bildirishnomalar 
     * foydalanuvchiga xalaqit bermasligi uchun 5 soniyadan so'ng yopiladi.
     */
    function bildirishnomalarniAvtomatikYopish() {
        const xabarlar = document.querySelectorAll('.alert-em-danger, .alert-em-success, .alert');

        xabarlar.forEach(function(xabar) {
            // 5000 millisoniya = 5 soniya
            setTimeout(function() {
                if (typeof bootstrap !== 'undefined') {
                    try {
                        // Bootstrap 5 Alert API orqali yopish
                        const yopuvchi = bootstrap.Alert.getOrCreateInstance(xabar);
                        if (yopuvchi) {
                            yopuvchi.close();
                            console.log("Bildirishnoma muddati tugadi va yopildi.");
                        }
                    } catch (xato) {
                        // Agar Bootstrap yuklanmagan bo'lsa, elementni shunchaki yashiramiz
                        xabar.style.display = 'none';
                    }
                } else {
                    xabar.style.display = 'none';
                }
            }, 5000);
        });
    }

    // Funksiyani ishga tushiramiz
    bildirishnomalarniAvtomatikYopish();


    /**
     * 3. JURNAL KATAKLARIGA INTERAKTIVLIK QO'SHISH
     * O'qituvchi jurnalidagi kataklar ustiga borganda ularni ajratib ko'rsatish.
     */
    // # IZOH: Jurnal sahifasida `.table-jurnal`, boshqa joylarda `.table-em` ishlatiladi.
    const jurnalKataklari = document.querySelectorAll('.table-em tbody td, .table-jurnal tbody td');
    jurnalKataklari.forEach(td => {
        td.addEventListener('mouseenter', function() {
            // Agar katak ichida baho qo'yish tugmasi bo'lsa, fonni o'zgartiramiz
            if (this.querySelector('button') || this.innerText.trim() !== "") {
                this.style.backgroundColor = 'rgba(0, 135, 192, 0.05)';
            }
        });

        td.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });


    /**
     * 4. CHART.JS UCHUN GLOBAL SOZLAMALAR (Ixtiyoriy)
     * Grafiklar o'zbek tilida va eMaktab ranglarida chiqishi uchun.
     */
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Open Sans', sans-serif";
        Chart.defaults.color = "#64748b";
        console.log("Grafik tizimi (Chart.js) tayyor holatda.");
    }

    /**
     * 5. PAROLNI KO'RSATISH/YASHIRISH (KO'ZCHA)
     * Login sahifasida foydalanuvchi parolni tekshirishi uchun qulaylik.
     */
    document.querySelectorAll("[data-bn-pass-target]").forEach((btn) => {
        if (btn.dataset.bnBound) return;
        btn.dataset.bnBound = "1";

        const targetId = btn.getAttribute("data-bn-pass-target");
        const input = targetId ? document.getElementById(targetId) : null;
        if (!input) return;

        btn.addEventListener("click", () => {
            const isHidden = input.type === "password";
            input.type = isHidden ? "text" : "password";

            const icon = btn.querySelector("i");
            if (icon) {
                icon.classList.toggle("bi-eye", !isHidden);
                icon.classList.toggle("bi-eye-slash", isHidden);
            }
        });
    });

});

/**
 * 5. PROFESSIONAL FORM VALIDATION (Tekshiruv)
 * Baho qo'yishda qiymatlarni (1-5 oralig'ida) tekshirish uchun yordamchi funksiya.
 */
function bahoniTekshir(qiymat) {
    if (qiymat < 1 || qiymat > 5) {
        alert("Xato: Baho 1 va 5 oralig'ida bo'lishi shart!");
        return false;
    }
    return true;
}
