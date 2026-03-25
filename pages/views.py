import csv
import json
from datetime import timedelta

f


from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView

from .decorators import driver_required, superuser_required
from .forms import (
    DriverApplicationForm,
    ForgotPasswordLookupForm,
    ProfileUpdateForm,
    RideBookingForm,
    RideMessageForm,
    RideOfferForm,
    RideSearchForm,
    SOSForm,
    TourBookingForm,
    UserRegistrationForm,
    UserVerificationForm,
    VehicleForm,
)
from .mixins import ApprovedDriverRequiredMixin, DriverRequiredMixin
from .models import (
    ContactMessage,
    Destination,
    DriverVerification,
    GuideRequest,
    Ride,
    RideBooking,
    RideMessage,
    RideReview,
    SOSAlert,
    Testimonial,
    Tour,
    TourBooking,
    UserProfile,
    Vehicle,
)
from .utils import (
    calculate_ride_price,
    calculate_user_rating,
    check_ride_availability,
    is_approved_driver,
    send_platform_notification,
    verification_status,
)

User = get_user_model()
PASSWORD_RESET_SESSION_KEY = "password_reset_user_id"


# Existing public pages

def home(request):
    featured_destinations = Destination.objects.filter(is_featured=True)[:6]
    featured_tours = Tour.objects.filter(is_active=True)[:6]
    return render(
        request,
        "pages/home_app.html",
        {
            "featured_destinations": featured_destinations,
            "featured_tours": featured_tours,
        },
    )



def health_check(request):
    return HttpResponse("OK", content_type="text/plain")



def about(request):
    return render(request, "pages/about_app.html")


@login_required
def destinations(request):
    destination_list = Destination.objects.all()
    return render(request, "pages/destinations_app.html", {"destination_list": destination_list})


@login_required
def destination_details(request, slug=None):
    destination = None
    related_rides = Ride.objects.none()
    if slug:
        destination = get_object_or_404(Destination, slug=slug)
        related_rides = Ride.objects.filter(
            Q(destination_location__icontains=destination.region) | Q(destination_location__icontains=destination.name),
            status=Ride.STATUS_SCHEDULED,
            departure_datetime__gt=timezone.now(),
        )
    return render(
        request,
        "pages/destination-details_app.html",
        {"destination": destination, "related_rides": related_rides},
    )


@login_required
def tours(request):
    tour_list = Tour.objects.filter(is_active=True)
    return render(request, "pages/tours_app.html", {"tour_list": tour_list})


@login_required
def tour_details(request, slug=None):
    tour = get_object_or_404(Tour, slug=slug) if slug else None
    return render(request, "pages/tour-details_app.html", {"tour": tour})


def gallery(request):
    return render(request, "pages/gallery.html")


def blog(request):
    return render(request, "pages/blog.html")


def blog_details(request):
    return render(request, "pages/blog-details.html")


def booking(request):
    return render(request, "pages/booking.html")


def testimonials(request):
    testimonial_list = Testimonial.objects.filter(is_published=True)
    return render(request, "pages/testimonials.html", {"testimonial_list": testimonial_list})


def faq(request):
    return render(request, "pages/faq.html")


@login_required
def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            full_name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            subject=request.POST.get("subject", "General Inquiry"),
            message=request.POST.get("message", ""),
        )
        messages.success(request, "Your message has been sent.")
        return redirect("contact")
    return render(request, "pages/contact_app.html")


def terms(request):
    return render(request, "pages/terms.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def starter_page(request):
    return render(request, "pages/starter-page.html")


def not_found(request):
    return render(request, "pages/404.html")


@login_required
def how_it_works(request):
    return render(request, "pages/how-it-works.html")


@login_required
def safety_tips(request):
    return render(request, "pages/safety-tips.html")


# Authentication & profiles

class SafariLoginView(LoginView):
    template_name = "pages/auth/login.html"


class SafariLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("dashboard")
    return render(request, "pages/auth/register.html", {"form": form})


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = ForgotPasswordLookupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["identifier"]
        user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        if not user:
            form.add_error("identifier", "No account found with that email or username.")
        else:
            request.session[PASSWORD_RESET_SESSION_KEY] = user.pk
            return redirect("forgot_password_reset")
    return render(request, "pages/auth/forgot_password.html", {"form": form})


def forgot_password_reset(request):
    user_id = request.session.get(PASSWORD_RESET_SESSION_KEY)
    if not user_id:
        messages.error(request, "Start password reset by entering your email or username.")
        return redirect("forgot_password")

    user = User.objects.filter(pk=user_id).first()
    if not user:
        request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
        messages.error(request, "Account not found. Start password reset again.")
        return redirect("forgot_password")

    form = SetPasswordForm(user=user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
        messages.success(request, "Password reset successful. You can now sign in.")
        return redirect("login")
    return render(request, "pages/auth/reset_password.html", {"form": form, "account_user": user})


@login_required
def dashboard(request):
    profile = request.user.profile
    recent_unread_messages = RideMessage.objects.filter(recipient=request.user, is_read=False).select_related(
        "sender", "ride"
    )[:6]
    context = {
        "profile": profile,
        "rides_offered": Ride.objects.filter(driver=request.user).count(),
        "ride_bookings": RideBooking.objects.filter(passenger=request.user).count(),
        "tour_bookings": TourBooking.objects.filter(traveler=request.user).count(),
        "unread_messages": RideMessage.objects.filter(recipient=request.user, is_read=False).count(),
        "recent_unread_messages": recent_unread_messages,
        "verification": verification_status(request.user),
    }
    return render(request, "pages/dashboard.html", context)


@login_required
def notifications(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_all_read":
            RideMessage.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
            messages.success(request, "All notifications marked as read.")
            return redirect("notifications")
        if action == "mark_read":
            msg = get_object_or_404(RideMessage, pk=request.POST.get("message_id"), recipient=request.user)
            if not msg.is_read:
                msg.is_read = True
                msg.save(update_fields=["is_read"])
            messages.success(request, "Notification marked as read.")
            return redirect("notifications")

    notifications_qs = RideMessage.objects.filter(recipient=request.user).select_related("sender", "ride").order_by(
        "-sent_at"
    )
    unread_count = notifications_qs.filter(is_read=False).count()
    return render(
        request,
        "pages/notifications.html",
        {"notifications": notifications_qs[:200], "unread_count": unread_count},
    )


@login_required
def profile_detail(request, username):
    user_obj = get_object_or_404(User, username=username)
    context = {
        "profile_user": user_obj,
        "profile": getattr(user_obj, "profile", None),
        "rating": calculate_user_rating(user_obj),
    }
    return render(request, "pages/profile-detail.html", context)


@login_required
def profile_update(request, username):
    if request.user.username != username:
        messages.error(request, "You can only edit your own profile.")
        return redirect("profile_detail", username=request.user.username)

    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile_detail", username=request.user.username)

    return render(request, "pages/profile-edit.html", {"form": form})


@login_required
def profile_verify(request, username):
    if request.user.username != username:
        messages.error(request, "You can only submit your own verification.")
        return redirect("profile_detail", username=request.user.username)

    instance, _ = DriverVerification.objects.get_or_create(driver=request.user)

    form = UserVerificationForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.background_check_status = DriverVerification.STATUS_PENDING
        obj.verified_badge = False
        obj.save()
        messages.success(request, "Verification submitted for review.")
        return redirect("dashboard")

    return render(request, "pages/driver-verification.html", {"form": form, "verification": instance})


# Ride-sharing

class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = "pages/find-ride.html"
    context_object_name = "rides"
    paginate_by = 10
    login_url = reverse_lazy("home")

    def get_queryset(self):
        qs = Ride.objects.filter(status=Ride.STATUS_SCHEDULED, departure_datetime__gt=timezone.now()).select_related(
            "driver", "vehicle"
        )
        self.search_form = RideSearchForm(self.request.GET or None)
        if self.search_form.is_valid():
            data = self.search_form.cleaned_data
            dep = data.get("departure_location")
            dest = data.get("destination_location")
            travel_date = data.get("travel_date")
            max_price = data.get("max_price")
            min_seats = data.get("min_seats")

            if dep:
                qs = qs.filter(departure_location__iexact=dep)
            if dest:
                qs = qs.filter(destination_location__iexact=dest)
            if travel_date:
                qs = qs.filter(departure_datetime__date=travel_date)
            if max_price:
                qs = qs.filter(price_per_seat__lte=max_price)
            if min_seats:
                qs = [ride for ride in qs if ride.seats_remaining >= min_seats]

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = getattr(self, "search_form", RideSearchForm())
        return context


class RideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = "pages/ride-detail.html"
    context_object_name = "ride"
    login_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ride = self.object
        ride.messages.filter(recipient=self.request.user, is_read=False).update(is_read=True)
        context["booking_form"] = RideBookingForm(ride=ride)
        context["message_form"] = RideMessageForm()
        context["driver_rating"] = calculate_user_rating(ride.driver)
        if self.request.user == ride.driver:
            thread_qs = ride.messages.select_related("sender", "recipient")[:50]
        else:
            thread_qs = (
                ride.messages.filter(
                    Q(sender=self.request.user, recipient=ride.driver)
                    | Q(sender=ride.driver, recipient=self.request.user)
                )
                .select_related("sender", "recipient")[:50]
            )
        context["messages_thread"] = thread_qs
        return context


class OfferRideView(ApprovedDriverRequiredMixin, CreateView):
    model = Ride
    form_class = RideOfferForm
    template_name = "pages/offer-ride.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["driver"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.driver = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Ride posted successfully.")
        return response

    def get_success_url(self):
        return reverse("ride_detail", kwargs={"pk": self.object.pk})


@login_required
@require_http_methods(["POST"])
def book_ride(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    form = RideBookingForm(request.POST, ride=ride)

    if not check_ride_availability(ride):
        messages.error(request, "This ride is no longer available.")
        return redirect("ride_detail", pk=pk)

    if form.is_valid():
        with transaction.atomic():
            seats = form.cleaned_data["seats_booked"]
            if not check_ride_availability(ride, seats):
                messages.error(request, "Seats changed while booking. Try again.")
                return redirect("ride_detail", pk=pk)

            pricing = calculate_ride_price(ride, seats)
            booking = RideBooking.objects.create(
                passenger=request.user,
                ride=ride,
                seats_booked=seats,
                total_price=pricing["total"],
                booking_status=RideBooking.STATUS_CONFIRMED,
                payment_status=RideBooking.PAYMENT_HELD,
            )

            send_platform_notification(
                request.user,
                "Ride booking confirmed",
                f"Your booking for ride #{ride.pk} is confirmed. Total: KES {booking.total_price}",
            )
            send_platform_notification(
                ride.driver,
                "New ride booking",
                f"{request.user.username} booked {seats} seat(s) on ride #{ride.pk}.",
            )

        messages.success(request, "Ride booked successfully.")
    else:
        messages.error(request, "Could not complete booking. Check input and retry.")

    return redirect("ride_detail", pk=pk)


@login_required
def my_bookings(request):
    bookings = RideBooking.objects.filter(passenger=request.user).select_related("ride", "ride__driver")
    return render(request, "pages/my-bookings.html", {"bookings": bookings})


@login_required
@driver_required
def my_rides(request):
    rides = Ride.objects.filter(driver=request.user).annotate(total_bookings=Count("bookings"))
    return render(request, "pages/my-rides.html", {"rides": rides})


@login_required
@require_http_methods(["POST"])
def cancel_ride_booking(request, pk):
    booking = get_object_or_404(RideBooking, pk=pk, passenger=request.user)
    if booking.booking_status == RideBooking.STATUS_CANCELLED:
        messages.info(request, "Booking already cancelled.")
        return redirect("my_bookings")

    booking.booking_status = RideBooking.STATUS_CANCELLED
    booking.payment_status = RideBooking.PAYMENT_REFUNDED
    booking.cancellation_reason = request.POST.get("reason", "Cancelled by user")
    booking.save(update_fields=["booking_status", "payment_status", "cancellation_reason", "updated_at"])

    messages.success(request, "Booking cancelled and refund initiated.")
    return redirect("my_bookings")


@login_required
@require_http_methods(["POST"])
def send_ride_message(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    form = RideMessageForm(request.POST)

    if form.is_valid():
        recipient = None
        recipient_id = request.POST.get("recipient_id")
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id)
        elif request.user != ride.driver:
            recipient = ride.driver

        if recipient is None or recipient == request.user:
            messages.error(request, "Choose a valid recipient to reply.")
            return redirect("ride_detail", pk=pk)

        if request.user == ride.driver:
            allowed_recipients = set(
                RideBooking.objects.filter(ride=ride).values_list("passenger_id", flat=True)
            )
            history_users = set(
                ride.messages.values_list("sender_id", flat=True)
            ) | set(ride.messages.values_list("recipient_id", flat=True))
            allowed_recipients = (allowed_recipients | history_users) - {ride.driver_id}
            if recipient.id not in allowed_recipients:
                messages.error(request, "You can only reply to users involved in this ride.")
                return redirect("ride_detail", pk=pk)
        else:
            if recipient != ride.driver:
                messages.error(request, "Passengers can only message the ride driver.")
                return redirect("ride_detail", pk=pk)

        RideMessage.objects.create(
            ride=ride,
            sender=request.user,
            recipient=recipient,
            body=form.cleaned_data["body"],
        )
        send_platform_notification(
            recipient,
            "New ride message",
            f"You have a new message from {request.user.username} on ride #{ride.pk}.",
        )
        messages.success(request, "Message sent.")

    return redirect("ride_detail", pk=pk)


@login_required
def vehicle_create(request):
    form = VehicleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        vehicle = form.save(commit=False)
        vehicle.driver = request.user
        vehicle.save()
        messages.success(request, "Vehicle added successfully.")
        return redirect("my_rides")
    return render(request, "pages/vehicle-form.html", {"form": form})


# Tour integration

@login_required
def create_tour_booking(request, slug):
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    form = TourBookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.tour = tour
        booking.traveler = request.user
        booking.status = TourBooking.STATUS_CONFIRMED
        booking.save()
        send_platform_notification(
            request.user,
            "Tour booking confirmed",
            f"Your booking for {tour.title} is confirmed for {booking.travel_date}.",
        )
        messages.success(request, "Tour booked successfully.")
        return redirect("tours")

    return render(request, "pages/tour-booking-form.html", {"form": form, "tour": tour})


@login_required
@driver_required
def become_guide(request):
    form = DriverApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        guide_request = form.save(commit=False)
        guide_request.driver = request.user
        guide_request.status = GuideRequest.STATUS_PENDING
        guide_request.save()
        messages.success(request, "Guide request submitted.")
        return redirect("dashboard")

    return render(request, "pages/guide-request.html", {"form": form})


# Safety

@login_required
def sos_alert(request):
    form = SOSForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        alert = form.save(commit=False)
        alert.user = request.user
        alert.status = SOSAlert.STATUS_OPEN
        alert.save()

        send_platform_notification(
            request.user,
            "SOS alert received",
            "We have logged your SOS alert and notified the safety team.",
        )
        messages.success(request, "SOS alert sent.")
        return redirect("dashboard")

    return render(request, "pages/sos.html", {"form": form})


# Admin dashboard (superuser only)

ADMIN_REVIEW_FLAG_KEYWORDS = ("scam", "fraud", "abuse", "thief", "stupid", "idiot")


def _admin_sidebar_counts():
    return {
        "pending_verifications_count": DriverVerification.objects.filter(
            background_check_status=DriverVerification.STATUS_PENDING
        ).count(),
        "open_sos_count": SOSAlert.objects.filter(status=SOSAlert.STATUS_OPEN).count(),
        "unread_contacts_count": ContactMessage.objects.filter(is_resolved=False).count(),
    }


def _admin_context(active_tab, **kwargs):
    context = {"active_tab": active_tab}
    context.update(_admin_sidebar_counts())
    context.update(kwargs)
    return context


@superuser_required
def admin_dashboard(request):
    today = timezone.localdate()
    now = timezone.now()
    month_start = today.replace(day=1)
    start_30 = now - timedelta(days=29)

    total_users = User.objects.count()
    drivers_count = UserProfile.objects.filter(user_type=UserProfile.USER_TYPE_DRIVER).count()
    passengers_count = UserProfile.objects.exclude(user_type=UserProfile.USER_TYPE_DRIVER).count()
    active_rides_today = Ride.objects.filter(
        departure_datetime__date=today,
        status__in=[Ride.STATUS_SCHEDULED, Ride.STATUS_IN_PROGRESS],
    ).count()
    pending_verifications = DriverVerification.objects.filter(
        background_check_status=DriverVerification.STATUS_PENDING
    ).count()
    bookings_this_month = RideBooking.objects.filter(created_at__date__gte=month_start).count()
    sos_last_24h = SOSAlert.objects.filter(created_at__gte=now - timedelta(hours=24)).count()
    unread_contacts = ContactMessage.objects.filter(is_resolved=False).count()

    signup_points = (
        User.objects.filter(date_joined__gte=start_30)
        .annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    signup_map = {point["day"]: point["total"] for point in signup_points}
    signup_labels = []
    signup_values = []
    for day_offset in range(30):
        day = (start_30 + timedelta(days=day_offset)).date()
        signup_labels.append(day.strftime("%b %d"))
        signup_values.append(signup_map.get(day, 0))

    route_points = (
        Ride.objects.values("departure_location", "destination_location")
        .annotate(total=Count("id"))
        .order_by("-total")[:8]
    )
    route_labels = [f"{row['departure_location']} -> {row['destination_location']}" for row in route_points]
    route_values = [row["total"] for row in route_points]

    booking_status_points = (
        RideBooking.objects.values("booking_status").annotate(total=Count("id")).order_by("booking_status")
    )
    booking_status_labels = [row["booking_status"].replace("_", " ").title() for row in booking_status_points]
    booking_status_values = [row["total"] for row in booking_status_points]

    context = _admin_context(
        "dashboard",
        total_users=total_users,
        drivers_count=drivers_count,
        passengers_count=passengers_count,
        active_rides_today=active_rides_today,
        pending_verifications=pending_verifications,
        bookings_this_month=bookings_this_month,
        sos_last_24h=sos_last_24h,
        unread_contacts=unread_contacts,
        signup_labels_json=json.dumps(signup_labels),
        signup_values_json=json.dumps(signup_values),
        route_labels_json=json.dumps(route_labels),
        route_values_json=json.dumps(route_values),
        booking_status_labels_json=json.dumps(booking_status_labels),
        booking_status_values_json=json.dumps(booking_status_values),
    )
    return render(request, "pages/admin/dashboard_home.html", context)


@superuser_required
def admin_users(request):
    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        user_obj = get_object_or_404(User, pk=user_id)

        if action == "suspend":
            if user_obj == request.user:
                messages.error(request, "You cannot suspend your own account.")
            else:
                user_obj.is_active = False
                user_obj.save(update_fields=["is_active"])
                messages.success(request, f"User {user_obj.username} suspended.")
        elif action == "activate":
            user_obj.is_active = True
            user_obj.save(update_fields=["is_active"])
            messages.success(request, f"User {user_obj.username} activated.")
        elif action == "delete":
            if user_obj == request.user:
                messages.error(request, "You cannot delete your own account.")
            else:
                username = user_obj.username
                user_obj.delete()
                messages.success(request, f"User {username} deleted.")
        return redirect("admin_users")

    users_qs = User.objects.select_related("profile").order_by("-date_joined")
    search = request.GET.get("search", "").strip()
    user_type = request.GET.get("user_type", "").strip()
    verified = request.GET.get("verified", "").strip()
    joined_from = request.GET.get("joined_from", "").strip()
    joined_to = request.GET.get("joined_to", "").strip()

    if search:
        users_qs = users_qs.filter(
            Q(username__icontains=search) | Q(email__icontains=search) | Q(profile__phone_number__icontains=search)
        )
    if user_type:
        users_qs = users_qs.filter(profile__user_type=user_type)
    if verified in {"yes", "no"}:
        users_qs = users_qs.filter(profile__is_verified=(verified == "yes"))
    if joined_from:
        users_qs = users_qs.filter(date_joined__date__gte=joined_from)
    if joined_to:
        users_qs = users_qs.filter(date_joined__date__lte=joined_to)

    verification_by_user = {v.driver_id: v for v in DriverVerification.objects.select_related("driver")}
    users = list(users_qs[:400])
    for user_obj in users:
        try:
            user_obj.admin_profile = user_obj.profile
        except Exception:
            user_obj.admin_profile = None
        user_obj.admin_verification = verification_by_user.get(user_obj.id)
    context = _admin_context(
        "users",
        users=users,
        filter_user_type=user_type,
        filter_verified=verified,
        filter_joined_from=joined_from,
        filter_joined_to=joined_to,
        filter_search=search,
    )
    return render(request, "pages/admin/users.html", context)


@superuser_required
def admin_rides(request):
    if request.method == "POST":
        action = request.POST.get("action")
        ride = get_object_or_404(Ride, pk=request.POST.get("ride_id"))
        if action == "cancel":
            ride.status = Ride.STATUS_CANCELLED
            ride.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Ride #{ride.pk} cancelled.")
        elif action == "contact_driver":
            messages.info(request, f"Contact driver at {ride.driver.email}.")
        return redirect("admin_rides")

    rides_qs = Ride.objects.select_related("driver", "vehicle").prefetch_related("bookings__passenger").order_by(
        "-created_at"
    )
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if status:
        rides_qs = rides_qs.filter(status=status)
    if date_from:
        rides_qs = rides_qs.filter(departure_datetime__date__gte=date_from)
    if date_to:
        rides_qs = rides_qs.filter(departure_datetime__date__lte=date_to)

    context = _admin_context(
        "rides",
        rides=rides_qs[:300],
        filter_status=status,
        filter_date_from=date_from,
        filter_date_to=date_to,
    )
    return render(request, "pages/admin/rides.html", context)


@superuser_required
def admin_bookings(request):
    if request.method == "POST":
        action = request.POST.get("action")
        booking = get_object_or_404(RideBooking, pk=request.POST.get("booking_id"))

        if action == "confirm":
            booking.booking_status = RideBooking.STATUS_CONFIRMED
            booking.payment_status = RideBooking.PAYMENT_HELD
            booking.save(update_fields=["booking_status", "payment_status", "updated_at"])
            messages.success(request, f"Booking #{booking.pk} confirmed.")
        elif action == "cancel":
            booking.booking_status = RideBooking.STATUS_CANCELLED
            booking.payment_status = RideBooking.PAYMENT_REFUNDED
            booking.save(update_fields=["booking_status", "payment_status", "updated_at"])
            messages.success(request, f"Booking #{booking.pk} cancelled.")
        elif action == "complete":
            booking.booking_status = RideBooking.STATUS_CONFIRMED
            booking.payment_status = RideBooking.PAYMENT_RELEASED
            booking.save(update_fields=["booking_status", "payment_status", "updated_at"])
            messages.success(request, f"Booking #{booking.pk} marked completed.")
        return redirect("admin_bookings")

    bookings_qs = RideBooking.objects.select_related("passenger", "ride", "ride__driver").order_by("-created_at")
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    if status:
        bookings_qs = bookings_qs.filter(booking_status=status)
    if date_from:
        bookings_qs = bookings_qs.filter(created_at__date__gte=date_from)
    if date_to:
        bookings_qs = bookings_qs.filter(created_at__date__lte=date_to)

    total_booking_value = bookings_qs.aggregate(total=Sum("total_price"))["total"] or 0
    context = _admin_context(
        "bookings",
        bookings=bookings_qs[:400],
        total_booking_value=total_booking_value,
        filter_status=status,
        filter_date_from=date_from,
        filter_date_to=date_to,
    )
    return render(request, "pages/admin/bookings.html", context)


@superuser_required
def admin_verifications(request):
    if request.method == "POST":
        action = request.POST.get("action")
        verification = get_object_or_404(DriverVerification, pk=request.POST.get("verification_id"))
        reason = request.POST.get("reason", "").strip()

        if action == "approve":
            verification.background_check_status = DriverVerification.STATUS_APPROVED
            verification.verified_badge = True
            verification.reviewed_at = timezone.now()
            verification.admin_notes = reason
            verification.save(
                update_fields=["background_check_status", "verified_badge", "reviewed_at", "admin_notes"]
            )
            UserProfile.objects.filter(user=verification.driver).update(
                is_verified=True,
                user_type=UserProfile.USER_TYPE_DRIVER,
            )
            send_mail(
                "Driver verification approved",
                "Your SafariConnect driver verification has been approved.",
                None,
                [verification.driver.email],
                fail_silently=True,
            )
            messages.success(request, f"Verification approved for {verification.driver.username}.")
        elif action == "reject":
            verification.background_check_status = DriverVerification.STATUS_REJECTED
            verification.verified_badge = False
            verification.reviewed_at = timezone.now()
            verification.admin_notes = reason or "Rejected by admin."
            verification.save(
                update_fields=["background_check_status", "verified_badge", "reviewed_at", "admin_notes"]
            )
            UserProfile.objects.filter(user=verification.driver).update(is_verified=False)
            send_mail(
                "Driver verification update",
                f"Your verification request was rejected. Reason: {verification.admin_notes}",
                None,
                [verification.driver.email],
                fail_silently=True,
            )
            messages.success(request, f"Verification rejected for {verification.driver.username}.")
        return redirect("admin_verifications")

    status = request.GET.get("status", DriverVerification.STATUS_PENDING).strip()
    verifications_qs = DriverVerification.objects.select_related("driver", "driver__profile").order_by("-submitted_at")
    if status in {DriverVerification.STATUS_PENDING, DriverVerification.STATUS_APPROVED, DriverVerification.STATUS_REJECTED}:
        verifications_qs = verifications_qs.filter(background_check_status=status)

    history = DriverVerification.objects.exclude(reviewed_at__isnull=True).select_related("driver").order_by("-reviewed_at")[:20]
    context = _admin_context(
        "verifications",
        verifications=verifications_qs[:200],
        verification_history=history,
        filter_status=status,
    )
    return render(request, "pages/admin/verifications.html", context)


@superuser_required
def admin_sos_alerts(request):
    if request.method == "POST":
        action = request.POST.get("action")
        alert = get_object_or_404(SOSAlert, pk=request.POST.get("alert_id"))
        if action == "resolve":
            alert.status = SOSAlert.STATUS_RESOLVED
            alert.save(update_fields=["status"])
            messages.success(request, f"SOS alert #{alert.pk} marked resolved.")
        elif action == "ack":
            alert.status = SOSAlert.STATUS_ACKNOWLEDGED
            alert.save(update_fields=["status"])
            messages.success(request, f"SOS alert #{alert.pk} acknowledged.")
        elif action == "contact":
            messages.info(request, f"Contact user at {alert.user.email}.")
        return redirect("admin_sos_alerts")

    status = request.GET.get("status", "").strip()
    alerts_qs = SOSAlert.objects.select_related("user", "ride").order_by("-created_at")
    if status:
        alerts_qs = alerts_qs.filter(status=status)

    context = _admin_context(
        "sos",
        alerts=alerts_qs[:300],
        filter_status=status,
    )
    return render(request, "pages/admin/sos_alerts.html", context)


@superuser_required
def admin_reviews(request):
    if request.method == "POST":
        action = request.POST.get("action")
        review = get_object_or_404(RideReview, pk=request.POST.get("review_id"))
        if action == "approve":
            messages.success(request, f"Review #{review.pk} approved.")
        elif action == "reject":
            review.delete()
            messages.success(request, "Review rejected and removed.")
        elif action == "delete":
            review.delete()
            messages.success(request, "Review deleted.")
        return redirect("admin_reviews")

    reviews_qs = RideReview.objects.select_related("reviewer", "reviewee", "booking").order_by("-created_at")
    flagged_ids = []
    for review in reviews_qs[:400]:
        text = (review.comment or "").lower()
        if any(word in text for word in ADMIN_REVIEW_FLAG_KEYWORDS):
            flagged_ids.append(review.pk)
    context = _admin_context("reviews", reviews=reviews_qs[:400], flagged_ids=flagged_ids)
    return render(request, "pages/admin/reviews.html", context)


@superuser_required
def admin_contact_messages(request):
    if request.method == "POST":
        action = request.POST.get("action")
        message_obj = get_object_or_404(ContactMessage, pk=request.POST.get("message_id"))
        if action == "mark_replied":
            message_obj.is_resolved = True
            message_obj.save(update_fields=["is_resolved"])
            messages.success(request, "Message marked as replied.")
        elif action == "quick_reply":
            reply_body = request.POST.get("reply_body", "").strip()
            if reply_body:
                send_mail(
                    f"Re: {message_obj.subject}",
                    reply_body,
                    None,
                    [message_obj.email],
                    fail_silently=True,
                )
                message_obj.is_resolved = True
                message_obj.save(update_fields=["is_resolved"])
                messages.success(request, "Reply sent and message marked as replied.")
            else:
                messages.error(request, "Reply text is required.")
        return redirect("admin_contact_messages")

    messages_qs = ContactMessage.objects.order_by("-created_at")
    status = request.GET.get("status", "").strip()
    if status in {"replied", "unread"}:
        messages_qs = messages_qs.filter(is_resolved=(status == "replied"))

    context = _admin_context(
        "contacts",
        contact_messages=messages_qs[:500],
        filter_status=status,
    )
    return render(request, "pages/admin/contact_messages.html", context)


@superuser_required
def admin_reports(request):
    export_type = request.GET.get("export", "").strip()
    if export_type in {"users", "rides", "bookings"}:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{export_type}_report.csv"'
        writer = csv.writer(response)

        if export_type == "users":
            writer.writerow(["ID", "Username", "Email", "Is Active", "Is Superuser", "Date Joined"])
            for u in User.objects.all().order_by("id"):
                writer.writerow([u.id, u.username, u.email, u.is_active, u.is_superuser, u.date_joined.isoformat()])
        elif export_type == "rides":
            writer.writerow(["ID", "Driver", "Route", "Departure", "Status", "Price/Seat", "Created"])
            for ride in Ride.objects.select_related("driver").all().order_by("id"):
                writer.writerow(
                    [
                        ride.id,
                        ride.driver.username,
                        f"{ride.departure_location} -> {ride.destination_location}",
                        ride.departure_datetime.isoformat(),
                        ride.status,
                        ride.price_per_seat,
                        ride.created_at.isoformat(),
                    ]
                )
        else:
            writer.writerow(["ID", "Passenger", "Ride ID", "Seats", "Status", "Payment", "Total Price", "Created"])
            for booking in RideBooking.objects.select_related("passenger", "ride").all().order_by("id"):
                writer.writerow(
                    [
                        booking.id,
                        booking.passenger.username,
                        booking.ride_id,
                        booking.seats_booked,
                        booking.booking_status,
                        booking.payment_status,
                        booking.total_price,
                        booking.created_at.isoformat(),
                    ]
                )
        return response

    top_drivers = (
        Ride.objects.filter(status=Ride.STATUS_COMPLETED)
        .values("driver__username")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    popular_dates = (
        RideBooking.objects.values(date=TruncDate("ride__departure_datetime"))
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    growth_points = (
        User.objects.annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    growth_labels = [row["day"].strftime("%Y-%m-%d") for row in growth_points]
    growth_values = [row["total"] for row in growth_points]

    context = _admin_context(
        "reports",
        top_drivers=top_drivers,
        popular_dates=popular_dates,
        growth_labels_json=json.dumps(growth_labels),
        growth_values_json=json.dumps(growth_values),
    )
    return render(request, "pages/admin/reports.html", context)


@staff_member_required
def custom_admin_dashboard(request):
    return redirect("admin_dashboard")


# Lightweight JSON APIs

@login_required
def api_rides(request):
    rides = Ride.objects.filter(status=Ride.STATUS_SCHEDULED, departure_datetime__gt=timezone.now())[:100]
    payload = [
        {
            "id": ride.pk,
            "driver": ride.driver.username,
            "departure_location": ride.departure_location,
            "destination_location": ride.destination_location,
            "departure_datetime": ride.departure_datetime.isoformat(),
            "price_per_seat": str(ride.price_per_seat),
            "seats_remaining": ride.seats_remaining,
        }
        for ride in rides
    ]
    return JsonResponse({"results": payload})


@login_required
def api_ride_availability(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    return JsonResponse(
        {
            "ride_id": ride.pk,
            "status": ride.status,
            "seats_remaining": ride.seats_remaining,
            "available": check_ride_availability(ride),
        }
    )


@login_required
def api_unread_notifications(request):
    unread_count = RideMessage.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({"unread_count": unread_count})
