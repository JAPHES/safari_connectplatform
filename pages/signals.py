from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserProfile
from .utils import send_platform_notification


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, phone_number="")
        send_platform_notification(
            instance,
            subject="Welcome to SafariConnect",
            body="Your account has been created. Complete profile verification to unlock all features.",
        )
    else:
        UserProfile.objects.get_or_create(user=instance, defaults={"phone_number": ""})


@receiver(post_save, sender=UserProfile)
def sync_admin_flags(sender, instance, **kwargs):
    if instance.user_type == "admin" and not instance.user.is_staff:
        instance.user.is_staff = True
        instance.user.is_superuser = instance.user.is_superuser or False
        instance.user.save(update_fields=["is_staff", "is_superuser"])
