from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Ride, RideBooking, UserProfile, Vehicle
from .utils import calculate_ride_price, check_ride_availability

User = get_user_model()


class RideModelTests(TestCase):
    def setUp(self):
        self.driver = User.objects.create_user(username="driver1", email="driver@example.com", password="pass12345")
        UserProfile.objects.filter(user=self.driver).update(user_type="driver", phone_number="0712345678")

    def test_route_validation_blocks_non_nairobi_mombasa(self):
        ride = Ride(
            driver=self.driver,
            departure_location="Nairobi",
            destination_location="Kisumu",
            departure_datetime=timezone.now() + timedelta(days=1),
            available_seats=3,
            price_per_seat=Decimal("2000.00"),
        )
        with self.assertRaises(ValidationError):
            ride.clean()

    def test_seats_remaining_updates_with_booking(self):
        ride = Ride.objects.create(
            driver=self.driver,
            departure_location="Nairobi",
            destination_location="Mombasa",
            departure_datetime=timezone.now() + timedelta(days=1),
            available_seats=3,
            price_per_seat=Decimal("2000.00"),
        )
        passenger = User.objects.create_user(username="passenger", email="p@example.com", password="pass12345")
        RideBooking.objects.create(passenger=passenger, ride=ride, seats_booked=2, booking_status="confirmed")

        self.assertEqual(ride.seats_remaining, 1)


class BookingFlowTests(TestCase):
    def setUp(self):
        self.driver = User.objects.create_user(username="driver2", email="driver2@example.com", password="pass12345")
        UserProfile.objects.filter(user=self.driver).update(user_type="driver", phone_number="0799999999")
        self.passenger = User.objects.create_user(username="passenger2", email="pass2@example.com", password="pass12345")

        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            make="Toyota",
            model="Hiace",
            color="White",
            plate_number="KDA123A",
            seat_capacity=14,
        )

        self.ride = Ride.objects.create(
            driver=self.driver,
            vehicle=self.vehicle,
            departure_location="Nairobi",
            destination_location="Mombasa",
            departure_datetime=timezone.now() + timedelta(days=1),
            available_seats=4,
            price_per_seat=Decimal("1800.00"),
        )

    def test_price_calculation_includes_commission(self):
        result = calculate_ride_price(self.ride, seats=2)
        self.assertEqual(result["base_amount"], Decimal("3600.00"))
        self.assertEqual(result["commission"], Decimal("360.00"))
        self.assertEqual(result["total"], Decimal("3960.00"))

    def test_ride_availability_helper(self):
        self.assertTrue(check_ride_availability(self.ride, seats_needed=2))

    def test_booking_total_price_saved(self):
        booking = RideBooking.objects.create(
            passenger=self.passenger,
            ride=self.ride,
            seats_booked=2,
            booking_status=RideBooking.STATUS_CONFIRMED,
            payment_status=RideBooking.PAYMENT_HELD,
        )
        self.assertEqual(booking.total_price, Decimal("3600.00"))
