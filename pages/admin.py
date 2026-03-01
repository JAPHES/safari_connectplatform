from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    ContactMessage,
    Destination,
    DriverVerification,
    GuideRequest,
    NewsletterSubscription,
    Ride,
    RideBooking,
    RideMessage,
    RideReview,
    SOSAlert,
    Testimonial,
    Tour,
    TourBooking,
    TourRidePackage,
    User,
    UserProfile,
    UserReport,
    Vehicle,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "is_active", "is_staff")
    search_fields = ("username", "email")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type", "phone_number", "is_verified", "is_email_verified")
    list_filter = ("user_type", "is_verified", "is_email_verified")
    search_fields = ("user__username", "phone_number", "id_number")


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "is_featured")
    list_filter = ("region", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "region")


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_days", "price", "is_active", "includes_ride_transfer")
    list_filter = ("is_active", "includes_ride_transfer")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)
    filter_horizontal = ("destinations",)


@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ("tour", "full_name", "travel_date", "travelers_count", "status")
    list_filter = ("status", "travel_date")
    search_fields = ("full_name", "email", "tour__title")


@admin.action(description="Approve selected driver verifications")
def approve_driver_verification(modeladmin, request, queryset):
    queryset.update(background_check_status=DriverVerification.STATUS_APPROVED, verified_badge=True)


@admin.register(DriverVerification)
class DriverVerificationAdmin(admin.ModelAdmin):
    list_display = ("driver", "background_check_status", "verified_badge", "submitted_at", "reviewed_at")
    list_filter = ("background_check_status", "verified_badge")
    search_fields = ("driver__username", "driver__email")
    actions = [approve_driver_verification]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "driver", "make", "model", "insurance_verified", "seat_capacity")
    list_filter = ("insurance_verified", "make")
    search_fields = ("plate_number", "driver__username")


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "driver",
        "departure_location",
        "destination_location",
        "departure_datetime",
        "available_seats",
        "price_per_seat",
        "status",
    )
    list_filter = ("status", "departure_location", "destination_location")
    search_fields = ("driver__username", "departure_location", "destination_location")


@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):
    list_display = ("ride", "passenger", "seats_booked", "total_price", "booking_status", "payment_status")
    list_filter = ("booking_status", "payment_status")
    search_fields = ("passenger__username", "ride__driver__username")


@admin.register(RideReview)
class RideReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "reviewer", "reviewee", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("reviewer__username", "reviewee__username")


@admin.register(RideMessage)
class RideMessageAdmin(admin.ModelAdmin):
    list_display = ("ride", "sender", "recipient", "is_read", "sent_at")
    list_filter = ("is_read",)
    search_fields = ("sender__username", "recipient__username")


@admin.register(GuideRequest)
class GuideRequestAdmin(admin.ModelAdmin):
    list_display = ("driver", "years_experience", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("driver__username",)


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "ride", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username",)


@admin.register(TourRidePackage)
class TourRidePackageAdmin(admin.ModelAdmin):
    list_display = ("tour", "ride", "package_price", "is_active")
    list_filter = ("is_active",)


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported_user", "is_resolved", "created_at")
    list_filter = ("is_resolved",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "rating", "is_published", "created_at")
    list_filter = ("is_published", "rating")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "is_resolved", "created_at")
    list_filter = ("is_resolved",)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
