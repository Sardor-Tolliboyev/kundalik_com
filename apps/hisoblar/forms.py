from django import forms
from django.contrib.auth import get_user_model


Foydalanuvchi = get_user_model()


class ShaxsiyProfilTahrirForm(forms.ModelForm):
    """
    Foydalanuvchi o'zining shaxsiy ma'lumotlarini tahrirlashi uchun forma.

    # IZOH: `username` (login) ataylab qo'shilmaydi — foydalanuvchi loginini o'zgartirmaydi.
    """

    class Meta:
        model = Foydalanuvchi
        fields = ("first_name", "last_name", "telefon", "telegram_id", "email")
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "telefon": "Telefon raqami",
            "telegram_id": "Telegram ID",
            "email": "Email",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
            "telefon": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "telegram_id": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
        }

