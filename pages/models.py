from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify


class User(AbstractUser):
    """Primary authentication model for SafariConnect."""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    USER_TYPE_TOURIST = "tourist"
    USER_TYPE_DRIVER = "driver"
    USER_TYPE_ADMIN = "admin"

    USER_TYPE_CHOICES = (
        (USER_TYPE_TOURIST, "Tourist/Traveler"),
        (USER_TYPE_DRIVER, "Driver"),
        (USER_TYPE_ADMIN, "Admin"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=30, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=USER_TYPE_TOURIST)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="profiles/avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"


class Destination(models.Model):
    name = models.CharField(max_length=150)
    region = models.CharField(max_length=120)
    description = models.TextField()
    highlights = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="destinations/heroes/", blank=True, null=True)
    gallery_image = models.ImageField(upload_to="destinations/gallery/", blank=True, null=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tour(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField()
    itinerary = models.TextField()
    duration_days = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    destinations = models.ManyToManyField(Destination, related_name="tours")
    max_group_size = models.PositiveIntegerField(default=12)
    includes_ride_transfer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TourBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="bookings")
    traveler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tour_bookings",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    travelers_count = models.PositiveIntegerField(default=1)
    travel_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.tour.title}"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client_name} ({self.rating}/5)"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name}: {self.subject}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class DriverVerification(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    driver = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_verification")
    national_id_upload = models.FileField(upload_to="verification/id_docs/", blank=True, null=True)
    driver_license_upload = models.FileField(upload_to="verification/licenses/", blank=True, null=True)
    insurance_upload = models.FileField(upload_to="verification/insurance/", blank=True, null=True)
    background_check_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    verified_badge = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Verification - {self.driver.username}"


class Vehicle(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles")
    make = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    year = models.PositiveIntegerField(blank=True, null=True)
    color = models.CharField(max_length=40)
    plate_number = models.CharField(max_length=30, unique=True)
    photo = models.ImageField(upload_to="vehicles/photos/", blank=True, null=True)
    insurance_verified = models.BooleanField(default=False)
    seat_capacity = models.PositiveIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["plate_number"]

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number})"


class Ride(models.Model):
    ROUTE_NAIROBI_MOMBASA = "NBO-MSA"

    STATUS_SCHEDULED = "scheduled"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rides")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name="rides", null=True, blank=True)
    departure_location = models.CharField(max_length=80)
    destination_location = models.CharField(max_length=80)
    route_code = models.CharField(max_length=20, default=ROUTE_NAIROBI_MOMBASA)
    departure_datetime = models.DateTimeField()
    available_seats = models.PositiveIntegerField(default=1)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    allow_luggage = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["departure_datetime"]

    def clean(self):
        route = {self.departure_location.strip().lower(), self.destination_location.strip().lower()}
        allowed = {"nairobi", "mombasa"}
        if route != allowed:
            raise ValidationError("Only Nairobi <-> Mombasa rides are supported currently.")
        if self.departure_datetime <= timezone.now():
            raise ValidationError("Ride departure must be in the future.")

    @property
    def seats_booked(self):
        booked = self.bookings.filter(
            booking_status__in=[RideBooking.STATUS_PENDING, RideBooking.STATUS_CONFIRMED]
        ).aggregate(total=Sum("seats_booked"))["total"]
        return booked or 0

    @property
    def seats_remaining(self):
        return max(self.available_seats - self.seats_booked, 0)

    def __str__(self):
        return f"{self.departure_location} to {self.destination_location} ({self.departure_datetime:%Y-%m-%d %H:%M})"


class RideBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    PAYMENT_PENDING = "pending"
    PAYMENT_HELD = "held"
    PAYMENT_RELEASED = "released"
    PAYMENT_REFUNDED = "refunded"

    BOOKING_STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_HELD, "Held"),
        (PAYMENT_RELEASED, "Released"),
        (PAYMENT_REFUNDED, "Refunded"),
    )

    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ride_bookings")
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="bookings")
    seats_booked = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    payment_reference = models.CharField(max_length=120, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.seats_booked < 1:
            raise ValidationError("You must book at least one seat.")

        if self.pk:
            existing = RideBooking.objects.get(pk=self.pk)
            prior = existing.seats_booked
        else:
            prior = 0

        if self.seats_booked - prior > self.ride.seats_remaining:
            raise ValidationError("Not enough seats available for this booking.")

    def save(self, *args, **kwargs):
        self.total_price = self.ride.price_per_seat * Decimal(self.seats_booked)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.passenger.username} - {self.ride}"


class RideReview(models.Model):
    booking = models.OneToOneField(RideBooking, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written")
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reviewer} -> {self.reviewee}: {self.rating}/5"


class RideMessage(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    body = models.TextField(max_length=1200)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"Message {self.sender} -> {self.recipient}"


class GuideRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="guide_requests")
    qualifications = models.TextField()
    years_experience = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Guide request - {self.driver.username}"


class SOSAlert(models.Model):
    STATUS_OPEN = "open"
    STATUS_ACKNOWLEDGED = "acknowledged"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = (
        (STATUS_OPEN, "Open"),
        (STATUS_ACKNOWLEDGED, "Acknowledged"),
        (STATUS_RESOLVED, "Resolved"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sos_alerts")
    ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, related_name="sos_alerts", null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SOS by {self.user.username} ({self.status})"


class TourRidePackage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="ride_packages")
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="tour_packages")
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tour", "ride")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tour.title} + {self.ride}"


class UserReport(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports_received")
    ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report: {self.reporter} -> {self.reported_user}"
