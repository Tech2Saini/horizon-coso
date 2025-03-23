from django import forms
from .models import MFASecret
from django.contrib.auth.models import User

class MFAUploadForm(forms.ModelForm):
    qr_code_image = forms.ImageField(label="Upload MFA QR Code")

    class Meta:
        model = MFASecret
        fields = ["qr_code_image"]
