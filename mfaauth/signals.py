import os
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import MFASecret

def delete_old_image(instance):
    """Helper function to delete old QR code image if it exists."""
    if instance.qr_code_image:  # Check if an image exists
        if os.path.isfile(instance.qr_code_image.path):  # Ensure the file exists
            os.remove(instance.qr_code_image.path)  # Delete the file

@receiver(pre_delete, sender=MFASecret)
def delete_qr_code_on_delete(sender, instance, **kwargs):
    """Delete QR code image when MFASecret record is deleted."""
    delete_old_image(instance)

@receiver(pre_save, sender=MFASecret)
def delete_qr_code_on_update(sender, instance, **kwargs):
    """Delete old QR code image when a new image is uploaded."""
    if instance.pk:  # Ensure this is an update, not a new record
        try:
            old_instance = MFASecret.objects.get(pk=instance.pk)
            if old_instance.qr_code_image != instance.qr_code_image:  # If the image is being changed
                delete_old_image(old_instance)
        except MFASecret.DoesNotExist:
            pass  # If the record doesn't exist yet, do nothing
