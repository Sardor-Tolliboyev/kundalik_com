from __future__ import annotations

from django.apps import AppConfig


class HisoblarConfig(AppConfig):
    """
    Foydalanuvchi hisoblarini boshqarish ilovasi sozlamalari.

    # IZOH: Admin yon menyusida ko'rinadigan sarlavha ham shu yerda beriladi.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hisoblar"
    verbose_name = "FOYDALANUVCHI HISOBLARI"

    def ready(self):
        """
        Ilova ishga tushganda `post_migrate` signaliga ulanadi.

        # IZOH: Bu loyiha faqat o'zbek tilida ishlaydi. Django admin'dagi Permission.name
        # (masalan: "Can add log entry") ba'zi joylarda inglizcha ko'rinib qolmasligi uchun
        # migratsiyadan so'ng permission nomlarini o'zbekchalashtirib qo'yamiz.
        """

        from django.db.models.signals import post_migrate

        post_migrate.connect(
            self._sync_permission_names_after_migrate,
            dispatch_uid="hisoblar_sync_perm_names_uz",
        )

    @staticmethod
    def _sync_permission_names_after_migrate(sender, **kwargs) -> None:
        """
        Migrate tugagach Permission.name maydonini o'zbekcha ko'rinishga moslaydi.

        # IZOH: Permission codename'lari o'zgarmaydi, faqat ko'rinadigan nomi (name) yangilanadi.
        """

        # Django permissions odatda `django.contrib.auth` post_migrate bosqichida yaratiladi.
        if not sender or getattr(sender, "name", "") != "django.contrib.auth":
            return

        from django.contrib.auth.models import Permission
        from django.db import transaction
        from django.db.utils import OperationalError, ProgrammingError

        prefix_to_uz = (
            ("Can add ", "Qo'shish mumkin"),
            ("Can change ", "O'zgartirish mumkin"),
            ("Can delete ", "O'chirish mumkin"),
            ("Can view ", "Ko'rish mumkin"),
        )

        def build_uz_name(permission_name: str, object_name: str) -> str | None:
            for prefix, action_uz in prefix_to_uz:
                if permission_name.startswith(prefix):
                    return f"{action_uz}: {object_name}"
            return None

        try:
            perms = Permission.objects.select_related("content_type").all()
        except (OperationalError, ProgrammingError):
            return

        with transaction.atomic():
            for perm in perms:
                new_name = build_uz_name(perm.name, perm.content_type.name)
                if new_name and perm.name != new_name:
                    perm.name = new_name
                    perm.save(update_fields=["name"])

