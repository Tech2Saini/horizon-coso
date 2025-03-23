from django.db import models
import uuid
import pyotp,time
from django.core.files.storage import default_storage



class MFASecret(models.Model):
    secret = models.CharField(max_length=100, unique=True,blank=True)  # Extracted MFA secret
    email = models.EmailField(max_length=70,unique=True,default='',blank=True)
    issuer = models.CharField(max_length=100,default='',blank=True)
    qr_code_image = models.ImageField(upload_to="mfa_qr_codes/", blank=True, null=True)  # Store QR image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # ✅ Auto-generate unique UUID

    def getotp(self):
        totp = pyotp.TOTP(self.secret)
        otp = totp.now()
        otp = totp.at(time.time())

        return otp
    