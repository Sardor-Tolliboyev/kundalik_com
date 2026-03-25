/**
 * Admin panel uchun kichik UI yaxshilovchi skriptlar.
 *
 * # IZOH: Ba'zi Django admin matnlari (masalan, nav-sidebar qidiruvi)
 * o'zbekchaga to'liq tarjima bo'lmaganda, shu yerda UI'ni o'zbekchalashtiramiz.
 */

function bnAdminInit() {
  // 0) Django admin theme toggle (quyosh/oy) tugmasi bizga kerak emas — butunlay olib tashlaymiz.
  // # IZOH: Django core template ichida chiqadigan elementni "o'chirish"ning eng xavfsiz yo'li — DOM'dan remove qilish.
  document.querySelectorAll(".theme-toggle, #header .theme-toggle").forEach((el) => el.remove());

  // 1) Chap menyudagi qidiruv inputi placeholder'ini o'zbekchalashtirish.
  const navSearch = document.querySelector('#nav-sidebar input[type="search"]');
  if (navSearch) {
    const placeholder = (navSearch.getAttribute("placeholder") || "").toLowerCase();
    if (placeholder.includes("start typing")) {
      navSearch.setAttribute("placeholder", "Qidirish uchun yozing...");
    }
  }

  // 2) Admin ichidagi file input'larni o'zbekchalashtirish (Choose file -> Fayl tanlash).
  document.querySelectorAll(".bn-file-input").forEach((input) => {
    const inputId = input.getAttribute("id");
    if (!inputId) return;

    const btn = document.querySelector(`[data-bn-file-btn="${inputId}"]`);
    const nameEl = document.querySelector(`[data-bn-file-name="${inputId}"]`);

    if (btn && !btn.dataset.bnBound) {
      btn.dataset.bnBound = "1";
      btn.addEventListener("click", () => input.click());
    }

    if (!input.dataset.bnBound) {
      input.dataset.bnBound = "1";
      input.addEventListener("change", () => {
        if (!nameEl) return;
        const fileName = input.files && input.files[0] ? input.files[0].name : "Fayl tanlanmadi";
        nameEl.textContent = fileName;
      });
    }
  });

  // 3) Django admin'da inglizcha bo'lib qolgan matnlarni oddiy (i18n'siz) o'zbekchalashtirish.
  // # IZOH: Django admin (uz) tarjimasi ayrim joylarda to'liq bo'lmagani uchun shu yondashuv tanlandi.
  const textMapExact = new Map([
    ["Home", "Bosh sahifa"],
    ["Run", "Bajarish"],
    ["Filter", "Filtr"],
    ["Show counts", "Soni ko'rsatilsin"],
    ["Hide counts", "Sonini yashirish"],
    ["Clear all filters", "Barcha filtrlarni tozalash"],
    ["Clear selection", "Tanlovni tozalash"],
    ["Save and add another", "Saqlash va yana qo'shish"],
    ["Save and continue editing", "Saqlash va tahrirni davom ettirish"],
    ["Save", "Saqlash"],
    ["Add", "Qo'shish"],
  ]);

  const replaceInText = (text) => {
    const t = (text || "").trim();
    return textMapExact.has(t) ? textMapExact.get(t) : null;
  };

  // Breadcrumbs: "Home" -> "Bosh sahifa"
  document.querySelectorAll(".breadcrumbs a").forEach((a) => {
    const mapped = replaceInText(a.textContent);
    if (mapped) a.textContent = mapped;
  });

  // Actions button: "Run" -> "Bajarish"
  document.querySelectorAll(".actions button[type='submit']").forEach((btn) => {
    const mapped = replaceInText(btn.textContent);
    if (mapped) btn.textContent = mapped;
  });

  // Actions select: ayrim tarjimalarda qo'shimcha bo'shliq sabab "Foydalanuvchilar larni" kabi ko'rinish chiqib qoladi.
  // # IZOH: Bu "larni/ni" qo'shimchalarini alohida so'z qilib yuboradigan tarjima muammosi.
  // Biz admin UI'da ko'rinish chiroyli bo'lishi uchun bo'shliqlarni yopishtirib qo'yamiz.
  document.querySelectorAll("select[name='action'] option").forEach((opt) => {
    const raw = (opt.textContent || "").replace(/\s+/g, " ").trim();
    if (!raw) return;
    const fixed = raw
      .replace(/\s+larni\b/gi, "larni")
      .replace(/\s+ni\b/gi, "ni")
      .replace(/\s+dan\b/gi, "dan")
      .replace(/\s+ga\b/gi, "ga");
    if (fixed !== raw) opt.textContent = fixed;
  });

  // Change list filter header: "Filter" -> "Filtr"
  const filterHeader = document.querySelector("#changelist-filter-header");
  if (filterHeader) {
    const mapped = replaceInText(filterHeader.textContent);
    if (mapped) filterHeader.textContent = mapped;
  }

  // Filter extra actions: "Show counts/Hide counts/Clear all filters"
  document.querySelectorAll("#changelist-filter-extra-actions a").forEach((a) => {
    const t = (a.textContent || "").replace(/\s+/g, " ").trim();
    // `× Clear all filters` kabi holatlarda faqat oxirgi qismni tekshiramiz.
    for (const [from, to] of textMapExact.entries()) {
      if (t === from) {
        a.textContent = to;
        break;
      }
      if (t.endsWith(from)) {
        a.textContent = t.slice(0, -from.length) + to;
        break;
      }
    }
  });

  // Filter summary: "By <title>" -> "<title> bo'yicha"
  document.querySelectorAll("details[data-filter-title] > summary").forEach((summary) => {
    const raw = (summary.textContent || "").replace(/\s+/g, " ").trim();
    const title = summary.closest("details")?.getAttribute("data-filter-title") || "";
    if (!title) return;

    // Django default: "By <title>" (tarjima bo'lmasa shunday qoladi)
    if (raw.toLowerCase().startsWith("by ")) {
      summary.textContent = `${title} bo'yicha`;
    }
  });

  // Sahifa sarlavhasi: "Select X to change/view" -> o'zbekcha.
  const h1 = document.querySelector("#content h1");
  if (h1) {
    const title = (h1.textContent || "").replace(/\s+/g, " ").trim();
    const changeMatch = title.match(/^Select (.+) to change$/i);
    const viewMatch = title.match(/^Select (.+) to view$/i);
    // # IZOH: Ba'zan model nomi atrofida bo'sh joylar kelib qoladi (masalan: "Foydalanuvchi ni").
    // Shuning uchun `trim()` qilib, tushum qo'shimchasini yopishtirib yozamiz.
    const tushum = (nom) => {
      const x = (nom || "").replace(/\s+/g, " ").trim();
      if (!x) return x;
      // Agar allaqachon "...ni" bilan tugasa, takrorlamaymiz.
      if (x.toLowerCase().endsWith("ni")) return x;
      return `${x}ni`;
    };
    if (changeMatch) h1.textContent = `Tahrirlash uchun ${tushum(changeMatch[1])} tanlang`;
    if (viewMatch) h1.textContent = `Ko'rish uchun ${tushum(viewMatch[1])} tanlang`;
  }

  // 4) User add form matni: "After you've created a user..." -> o'zbekcha
  document.querySelectorAll("#content p, #content .help, #content .helptext, #content .form-row p").forEach((el) => {
    const t = (el.textContent || "").replace(/\s+/g, " ").trim();
    if (t === "After you’ve created a user, you’ll be able to edit more user options." || t === "After you've created a user, you'll be able to edit more user options.") {
      el.textContent = "Foydalanuvchini yaratganingizdan so'ng, qo'shimcha sozlamalarni tahrirlashingiz mumkin bo'ladi.";
    }
  });

  // 5) Parol validator yordam matnlari (admin add/change form)
  const passwordHelpMap = new Map([
    ["Your password can’t be too similar to your other personal information.", "Parolingiz shaxsiy ma'lumotlaringizga juda o'xshash bo'lmasin."],
    ["Your password can't be too similar to your other personal information.", "Parolingiz shaxsiy ma'lumotlaringizga juda o'xshash bo'lmasin."],
    ["Your password must contain at least 8 characters.", "Parol kamida 8 ta belgidan iborat bo'lishi kerak."],
    ["Your password can’t be a commonly used password.", "Parol juda ommabop parol bo'lmasin."],
    ["Your password can't be a commonly used password.", "Parol juda ommabop parol bo'lmasin."],
    ["Your password can’t be entirely numeric.", "Parol faqat raqamlardan iborat bo'lmasin."],
    ["Your password can't be entirely numeric.", "Parol faqat raqamlardan iborat bo'lmasin."],
  ]);
  document.querySelectorAll("#content .help li, #content ul li").forEach((li) => {
    const t = (li.textContent || "").replace(/\s+/g, " ").trim();
    if (passwordHelpMap.has(t)) li.textContent = passwordHelpMap.get(t);
  });

  // 5.5) Admin parol sahifasida qolib ketgan inglizcha matnlar (parolni yangilash/OTP bloklari)
  // # IZOH: Ba'zi paketlar yoki Django admin sahifalarida (password form) matnlar inglizcha bo'lib qolishi mumkin.
  document.querySelectorAll("#content p, #content label, #content span, #content div").forEach((el) => {
    const raw = (el.textContent || "").replace(/\s+/g, " ").trim();
    if (!raw) return;

    // "Enter a new password for the user X."
    const m = raw.match(/^Enter a new password for the user (.+)\.$/i);
    if (m) {
      el.textContent = `Foydalanuvchi uchun yangi parol kiriting: ${m[1]}.`;
      return;
    }

    if (raw === "Password-based authentication:") {
      el.textContent = "Parol orqali kirish:";
      return;
    }

    if (raw === "Enabled") {
      el.textContent = "Yoqilgan";
      return;
    }

    if (raw === "Disabled") {
      el.textContent = "O‘chirilgan";
      return;
    }

    // Izoh matni (ko‘p bo‘lgani uchun startsWith bilan)
    if (
      raw.startsWith("Whether the user will be able to authenticate using a password or not.") ||
      raw.startsWith("If disabled, they may still be able to authenticate using other backends")
    ) {
      el.textContent =
        "Foydalanuvchi parol orqali tizimga kira oladimi-yo‘qmi shuni belgilaydi. " +
        "Agar o‘chirilsa, foydalanuvchi boshqa kirish usullari (masalan, SSO yoki LDAP) orqali baribir tizimga kira olishi mumkin.";
      return;
    }
  });

  // 6) Submit tugmalari (Save and add another, Save and continue editing, Save)
  document.querySelectorAll(".submit-row input[type='submit'], .submit-row button[type='submit']").forEach((el) => {
    const current = el.value ?? el.textContent;
    const mapped = replaceInText(current);
    if (!mapped) return;
    if (el.tagName.toLowerCase() === "input") el.value = mapped;
    else el.textContent = mapped;
  });

  // 7) Errornote: "Please correct the error(s) below." -> o'zbekcha
  document.querySelectorAll("#content .errornote").forEach((p) => {
    const t = (p.textContent || "").replace(/\s+/g, " ").trim();
    if (t === "Please correct the error below." || t === "Please correct the errors below.") {
      p.textContent = "Iltimos, quyidagi xatolarni to'g'rilang.";
    }
  });

  // 8) Admin parol ko'zchasi (O'CHIRILDI)
  // # IZOH: Foydalanuvchi talabiga ko'ra admin formalarda parol ko'rsatish ikonkalari ortiqcha bo'lgani uchun olib tashlandi.

  // 9) Huquqlar widgeti (FilteredSelectMultiple) ichida qolib ketgan inglizcha matnlar
  // # IZOH: Bu widget Django admin JS tomonidan keyinroq ham DOM'ga qayta yozilishi mumkin.
  // Shu sababli tarjimani bir necha marta va MutationObserver orqali ham qo'llaymiz.
  const bnTranslatePermissionsWidget = () => {
    const replacePrefix = (text, fromPrefix, toPrefix) => {
      const t = (text || "").trim();
      if (!t.toLowerCase().startsWith(fromPrefix.toLowerCase())) return null;
      return toPrefix + t.slice(fromPrefix.length);
    };

    const translateChooserHelp = (raw) => {
      const t = (raw || "").replace(/\s+/g, " ").trim();
      if (!t) return null;

      const toTushum = (objName) => {
        const x = (objName || "").trim();
        if (!x) return x;
        if (x.toLowerCase().endsWith("huquqlari")) {
          return x.slice(0, -"huquqlari".length) + "huquqlarini";
        }
        return x.toLowerCase().endsWith("ni") ? x : `${x}ni`;
      };

      const m = t.match(
        /^(Choose|Remove)\s+(.+?)\s+by selecting them and then select the\s+[\"“”']?(Choose|Remove)[\"“”']?\s+arrow button\.?$/i
      );
      if (m) {
        const amal = m[1].toLowerCase();
        const obyektNomi = m[2].trim();
        if (amal === "choose") {
          return `Tanlash uchun ro'yxatdan ${toTushum(obyektNomi)} belgilang va so'ng o'rtadagi "Tanlash" tugmasini bosing.`;
        }
        return `Olib tashlash uchun ro'yxatdan ${toTushum(obyektNomi)} belgilang va so'ng o'rtadagi "Olib tashlash" tugmasini bosing.`;
      }

      return null;
    };

    document
      .querySelectorAll(
        ".selector a, .selector button, .selector input[type='button'], .selector input[type='submit'], .selector .help, .selector p, .selector span"
      )
      .forEach((el) => {
        const rawValue = el instanceof HTMLInputElement ? (el.value || "") : "";

        if (el instanceof HTMLInputElement && rawValue) {
          const mappedChooseAll = replacePrefix(rawValue, "Choose all ", "Barchasini tanlash: ");
          if (mappedChooseAll) {
            el.value = mappedChooseAll;
            return;
          }
          const mappedRemoveAll = replacePrefix(rawValue, "Remove all ", "Barchasini olib tashlash: ");
          if (mappedRemoveAll) {
            el.value = mappedRemoveAll;
            return;
          }
          if (rawValue === "Choose") el.value = "Tanlash";
          if (rawValue === "Remove") el.value = "Olib tashlash";
          return;
        }

        const raw = (el.textContent || "").replace(/\s+/g, " ").trim();
        if (!raw) return;

        const translatedHelp = translateChooserHelp(raw);
        if (translatedHelp) {
          el.textContent = translatedHelp;
          return;
        }

        const mappedChooseAll = replacePrefix(raw, "Choose all ", "Barchasini tanlash: ");
        if (mappedChooseAll) {
          el.textContent = mappedChooseAll;
          return;
        }

        const mappedRemoveAll = replacePrefix(raw, "Remove all ", "Barchasini olib tashlash: ");
        if (mappedRemoveAll) {
          el.textContent = mappedRemoveAll;
          return;
        }

        if (raw === "Choose") el.textContent = "Tanlash";
        if (raw === "Remove") el.textContent = "Olib tashlash";
      });

    document.querySelectorAll(".selector [title]").forEach((el) => {
      const t = (el.getAttribute("title") || "").replace(/\s+/g, " ").trim();
      if (!t) return;

      if (t.includes('select the "Remove" arrow button')) {
        el.setAttribute(
          "title",
          "Olib tashlash uchun ro'yxatdan tanlang va so'ng o'rtadagi \"Olib tashlash\" tugmasini bosing."
        );
      }
      if (t.includes('select the "Choose" arrow button')) {
        el.setAttribute(
          "title",
          "Tanlash uchun ro'yxatdan tanlang va so'ng o'rtadagi \"Tanlash\" tugmasini bosing."
        );
      }
    });
  };

  // Darhol + keyinroq yana (Django admin JS DOM'ni qayta yozishi mumkin)
  bnTranslatePermissionsWidget();
  setTimeout(bnTranslatePermissionsWidget, 250);
  setTimeout(bnTranslatePermissionsWidget, 1200);

  // DOM o'zgarsa ham qayta tarjima qilish (huquqlar widgeti kech init bo'lganda)
  const contentRoot = document.querySelector("#content") || document.body;
  if (contentRoot && !contentRoot.dataset.bnPermObserver) {
    contentRoot.dataset.bnPermObserver = "1";
    const obs = new MutationObserver(() => {
      // Juda ko'p chaqirilmasligi uchun mikro-debounce
      if (contentRoot.dataset.bnPermTick) return;
      contentRoot.dataset.bnPermTick = "1";
      setTimeout(() => {
        contentRoot.dataset.bnPermTick = "";
        bnTranslatePermissionsWidget();
      }, 50);
    });
    obs.observe(contentRoot, { subtree: true, childList: true, characterData: true });
  }

  // 10) Parol blokida "Reset password" inglizcha bo'lib qolsa, o'zbekchalashtiramiz.
  document.querySelectorAll("#content a, #content button, #content input[type='submit']").forEach((el) => {
    const raw = el instanceof HTMLInputElement ? (el.value || "") : (el.textContent || "");
    const t = raw.replace(/\s+/g, " ").trim();
    if (!t) return;
    if (t === "Reset password") {
      if (el instanceof HTMLInputElement) el.value = "Parolni yangilash";
      else el.textContent = "Parolni yangilash";
    }
  });

  // 11) "Biriktirilgan farzandi" maydoni faqat ota-ona rolida ko'rinsin
  // # IZOH: Admin foydalanuvchi formasida `farzandi` fieldi faqat `rol='ota_ona'` bo'lganda kerak.
  const rolSelect = document.querySelector("#id_rol");
  const farzandInput = document.querySelector("#id_farzandi");
  const farzandRow = farzandInput ? farzandInput.closest(".form-row") : null;

  const bnUpdateFarzandVisibility = () => {
    if (!rolSelect || !farzandRow) return;
    const rol = (rolSelect.value || "").trim();
    const kerakmi = rol === "ota_ona";
    farzandRow.style.display = kerakmi ? "" : "none";
    if (!kerakmi && farzandInput) {
      // Rol ota-ona bo'lmasa, farzand tanlovini tozalab qo'yamiz (xato saqlanmasin).
      farzandInput.value = "";
    }
  };

  if (rolSelect && farzandRow) {
    bnUpdateFarzandVisibility();
    rolSelect.addEventListener("change", bnUpdateFarzandVisibility);
  }

  // 12) O'chirishni tasdiqlash sahifasi (delete_selected) matnlarini o'zbekchalashtirish
  // # IZOH: Django admin delete confirmation sahifasi ba'zan inglizcha bo'lib qoladi.
  // Buni template o'zgartirmasdan, oddiy JS bilan o'zbekchalaymiz.
  const pageH1 = document.querySelector("#content h1");
  if (pageH1) {
    const t = (pageH1.textContent || "").replace(/\s+/g, " ").trim();
    if (t === "Delete multiple objects") pageH1.textContent = "Bir nechta obyektni o'chirish";
    if (t === "Delete object") pageH1.textContent = "Obyektni o'chirish";
  }

  document.querySelectorAll("#content p, #content h2, #content h3, #content a, #content input[type='submit'], #content button").forEach((el) => {
    const isInput = el instanceof HTMLInputElement;
    const raw = isInput ? (el.value || "") : (el.textContent || "");
    const t = raw.replace(/\s+/g, " ").trim();
    if (!t) return;

    // Tugmalar
    if (/^Yes,\s*I[’']?m\s*sure$/i.test(t)) {
      if (isInput) el.value = "Ha, o'chiraman";
      else el.textContent = "Ha, o'chiraman";
      return;
    }
    if (/^No,\s*take\s*me\s*back$/i.test(t)) {
      if (isInput) el.value = "Yo'q, ortga qaytish";
      else el.textContent = "Yo'q, ortga qaytish";
      return;
    }

    // Asosiy ogohlantirish matni (model nomlari bo'lishi mumkin, shuning uchun partial match)
    if (t.startsWith("Are you sure you want to delete the selected") && t.includes("All of the following objects")) {
      // Model nomini ajratib olishga urinib ko'ramiz: "... selected X? All ..."
      const m = t.match(/^Are you sure you want to delete the selected (.+?)\\? All of the following objects/i);
      const nom = m && m[1] ? m[1].replace(/\?/g, "").trim() : "obyektlar";
      const yangisi = `Tanlangan ${nom}ni o'chirmoqchimisiz?`;
      if (isInput) el.value = yangisi;
      else el.textContent = yangisi;
      return;
    }

    // Bitta obyektni o'chirish sahifasi: "... delete the Sinf “5-sinf”? All of the following related items will be deleted:"
    if (t.toLowerCase().startsWith("are you sure you want to delete the ") && t.includes("related items will be deleted")) {
      const m = t.match(/^Are you sure you want to delete the (.+?)\\?\\s*All of the following related items will be deleted:?$/i);
      const nom = m && m[1] ? m[1].replace(/\s+/g, " ").trim() : "ushbu obyekt";
      const yangisi = `Rostdan ham ${nom} o'chirilsinmi?`;
      if (isInput) el.value = yangisi;
      else el.textContent = yangisi;
      return;
    }
  });

  // 12.1) O'chirish sahifasida keraksiz uzun ro'yxatlar ko'rinmasin (faqat tasdiqlash qolsin)
  // # IZOH: Userga faqat tasdiqlash tugmalari va qisqa ogohlantirish kifoya.
  if (document.body.classList.contains("delete-confirmation")) {
    // "Xulosa/Objects" sarlavhalarini yashirish
    document.querySelectorAll("#content h2, #content h3").forEach((h) => {
      const t = (h.textContent || "").replace(/\s+/g, " ").trim().toLowerCase();
      if (t === "xulosa" || t === "objects" || t === "obyektlar" || t === "summary") {
        h.style.display = "none";
      }
    });

    // Uzun ro'yxatlarni yashirish (submit-row ichidagilarga tegmaymiz)
    document.querySelectorAll("#content ul").forEach((ul) => {
      if (ul.closest(".submit-row")) return;
      if (ul.classList.contains("messagelist")) return;
      if (ul.classList.contains("errorlist")) return;
      ul.style.display = "none";
    });
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bnAdminInit);
} else {
  bnAdminInit();
}
