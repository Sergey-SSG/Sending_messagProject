from django import forms

from .models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "status", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "recipients": forms.CheckboxSelectMultiple(),
        }
