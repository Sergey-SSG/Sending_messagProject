from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите ваш номер телефона.",
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password1",
            "password2",
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class CustomUserChangeForm(UserChangeForm):
    password = None  # скрываем поле пароля

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "phone_number", "avatar")
