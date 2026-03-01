from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
from django.db.models import Q
from django.utils import timezone

from .models import (
    DriverVerification,
    GuideRequest,
    Ride,
    RideBooking,
    RideMessage,
    SOSAlert,
    TourBooking,
    UserProfile,
    Vehicle,
)

User = get_user_model()


class BootstrapFormMixin:
    """Apply Bootstrap 5 classes to rendered form fields."""

    def _apply_bootstrap(self):
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, (forms.FileInput,)):
                widget.attrs["class"] = "form-control"
            else:
                existing = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide default rules text; validation errors still appear when input is invalid.
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "phone_number",
            "id_number",
            "user_type",
            "avatar",
            "bio",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]


class RideOfferForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            "vehicle",
            "departure_location",
            "destination_location",
            "departure_datetime",
            "available_seats",
            "price_per_seat",
            "allow_luggage",
            "notes",
        ]
        widgets = {
            "departure_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, driver=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = driver
        if driver:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(driver=driver)

    def clean(self):
        cleaned = super().clean()
        dep = cleaned.get("departure_location", "").strip().lower()
        dest = cleaned.get("destination_location", "").strip().lower()
        allowed = {"nairobi", "mombasa"}

        if {dep, dest} != allowed:
            raise ValidationError("Only Nairobi and Mombasa route is supported currently.")

        dt = cleaned.get("departure_datetime")
        if dt and dt <= timezone.now():
            raise ValidationError("Departure must be in the future.")

        seats = cleaned.get("available_seats")
        if seats and seats > 14:
            raise ValidationError("Maximum 14 seats per ride for now.")

        return cleaned


class RideSearchForm(BootstrapFormMixin, forms.Form):
    departure_location = forms.ChoiceField(
        choices=(("nairobi", "Nairobi"), ("mombasa", "Mombasa")), required=False
    )
    destination_location = forms.ChoiceField(
        choices=(("mombasa", "Mombasa"), ("nairobi", "Nairobi")), required=False
    )
    travel_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=10, min_value=1)
    min_seats = forms.IntegerField(required=False, min_value=1)


class RideBookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RideBooking
        fields = ["seats_booked"]

    def __init__(self, *args, ride=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ride = ride
        if ride is not None:
            # Bind the FK early so ModelForm/model validation can safely access self.instance.ride.
            self.instance.ride = ride

    def clean_seats_booked(self):
        seats = self.cleaned_data["seats_booked"]
        if not self.ride:
            return seats
        if seats > self.ride.seats_remaining:
            raise ValidationError("Requested seats exceed available seats.")
        return seats


class VehicleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["make", "model", "year", "color", "plate_number", "photo", "seat_capacity"]


class UserVerificationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DriverVerification
        fields = ["national_id_upload", "driver_license_upload", "insurance_upload"]


class DriverApplicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GuideRequest
        fields = ["qualifications", "years_experience"]


class SOSForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SOSAlert
        fields = ["ride", "latitude", "longitude", "message"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["ride"].queryset = Ride.objects.filter(
                Q(bookings__passenger=user) | Q(driver=user)
            ).distinct()


class RideMessageForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RideMessage
        fields = ["body"]


class TourBookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TourBooking
        fields = ["full_name", "email", "phone_number", "travelers_count", "travel_date", "special_requests"]
        widgets = {
            "travel_date": forms.DateInput(attrs={"type": "date"}),
        }
