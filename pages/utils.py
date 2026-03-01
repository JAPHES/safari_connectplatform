from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.utils import timezone

from .models import RideReview


def calculate_ride_price(ride, seats, commission_rate=Decimal("0.10")):
    """Calculate gross amount plus platform commission for a ride booking."""
    base_amount = ride.price_per_seat * Decimal(seats)
    commission = base_amount * Decimal(commission_rate)
    total = base_amount + commission
    return {
        "base_amount": base_amount.quantize(Decimal("0.01")),
        "commission": commission.quantize(Decimal("0.01")),
        "total": total.quantize(Decimal("0.01")),
    }


def check_ride_availability(ride, seats_needed=1):
    if ride.status != "scheduled":
        return False
    if ride.departure_datetime <= timezone.now():
        return False
    return ride.seats_remaining >= seats_needed


def send_platform_notification(user, subject, body, fail_silently=True):
    """Basic email notification helper; can be delegated to Celery tasks later."""
    if not user.email:
        return False

    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@safariconnect.co.ke"),
        recipient_list=[user.email],
        fail_silently=fail_silently,
    )
    return True


def calculate_user_rating(user):
    result = RideReview.objects.filter(reviewee=user).aggregate(avg=Avg("rating"))
    return round(result["avg"], 2) if result["avg"] is not None else 0.0


def verification_status(user):
    profile = getattr(user, "profile", None)
    verification = getattr(user, "driver_verification", None)
    return {
        "profile_verified": bool(profile and profile.is_verified),
        "email_verified": bool(profile and profile.is_email_verified),
        "driver_verified": bool(verification and verification.verified_badge),
        "background_check_status": getattr(verification, "background_check_status", "not_submitted"),
    }


def is_approved_driver(user):
    """True when user is fully approved to offer rides."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    profile = getattr(user, "profile", None)
    verification = getattr(user, "driver_verification", None)
    return bool(
        profile
        and profile.user_type == "driver"
        and profile.is_verified
        and verification
        and verification.verified_badge
        and verification.background_check_status == "approved"
    )
