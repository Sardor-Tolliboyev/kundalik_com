/**
 * Haftalik dars jadvali sahifasi uchun admin modali.
 *
 * # IZOH: Admin/xodimlar jadval ichidan dars qo'shishi yoki tahrirlashi uchun.
 */

document.addEventListener("DOMContentLoaded", () => {
  const modalEl = document.getElementById("taqsimotModal");
  if (!modalEl) return;

  const titleEl = document.getElementById("taqsimotModalTitle");
  const submitBtn = document.getElementById("taqsimotSubmitBtn");

  const idInput = document.getElementById("taqsimot_id");
  const redirectInput = document.getElementById("redirect_to");

  const sinfSelect = document.getElementById("sinf_id");
  const fanSelect = document.getElementById("fan_id");
  const oqituvchiSelect = document.getElementById("oqituvchi_id");
  const kunSelect = document.getElementById("kun");
  const soatInput = document.getElementById("soat");

  modalEl.addEventListener("show.bs.modal", (event) => {
    const trigger = event.relatedTarget;
    if (!trigger) return;

    const mode = trigger.getAttribute("data-mode") || "create";
    const redirectTo = trigger.getAttribute("data-redirect") || redirectInput?.value || "";
    if (redirectInput) redirectInput.value = redirectTo;

    if (mode === "edit") {
      if (titleEl) titleEl.textContent = "Darsni tahrirlash";
      if (submitBtn) submitBtn.textContent = "Saqlash";

      if (idInput) idInput.value = trigger.getAttribute("data-id") || "";
      if (sinfSelect) sinfSelect.value = trigger.getAttribute("data-sinf") || "";
      if (fanSelect) fanSelect.value = trigger.getAttribute("data-fan") || "";
      if (oqituvchiSelect) oqituvchiSelect.value = trigger.getAttribute("data-oqituvchi") || "";
      if (kunSelect) kunSelect.value = trigger.getAttribute("data-kun") || "1";
      if (soatInput) soatInput.value = trigger.getAttribute("data-soat") || "";
      return;
    }

    // create mode
    if (titleEl) titleEl.textContent = "Dars qo'shish";
    if (submitBtn) submitBtn.textContent = "Qo'shish";
    if (idInput) idInput.value = "";

    // Agar cell ichidan bosilgan bo'lsa, kun/soat oldindan to'ldiriladi.
    const kun = trigger.getAttribute("data-kun");
    const soat = trigger.getAttribute("data-soat");
    if (kunSelect && kun) kunSelect.value = kun;
    if (soatInput && soat) soatInput.value = soat;
  });
});
