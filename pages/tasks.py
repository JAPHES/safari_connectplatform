from .utils import send_platform_notification


def send_ride_reminder_email(user, ride):
    """Placeholder Celery task body for reminder notifications."""
    subject = f"Reminder: Your ride departs on {ride.departure_datetime:%Y-%m-%d %H:%M}"
    body = f"Ride from {ride.departure_location} to {ride.destination_location} is coming up."
    return send_platform_notification(user, subject, body)
