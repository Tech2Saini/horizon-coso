from django.contrib import admin
from .models import MFASecret
from django.utils.html import format_html


class MFASecretAdmin(admin.ModelAdmin):
    list_display = ("email", "issuer",'key','secret','showQrCode')  # ✅ Show extracted fields
    readonly_fields = ("secret", "issuer")  # ✅ Make extracted fields read-only
    
    search_fields = ['email','issuer']
    def get_fields(self, request, obj=None):
        """Only show QR code field when adding; show all fields as read-only after saving."""
        if obj:  # Editing an existing entry
            return ("qr_code_image", "email", "issuer", "secret")
        return ("qr_code_image",)  # Only show QR upload when adding

    def save_model(self, request, obj, form, change):
        """Ensure secret, email, and issuer are extracted when admin saves."""
        obj.save()  # ✅ Calls model's save() method to extract QR data
    
    def showQrCode(self,instance):
        image = f'''<a href="{instance.qr_code_image.url}"><img width="100px" height="100px" src="{instance.qr_code_image.url}" />'''
        return  format_html(image)

admin.site.register(MFASecret, MFASecretAdmin)
