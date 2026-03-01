from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("destinations/", views.destinations, name="destinations"),
    path("destinations/<slug:slug>/", views.destination_details, name="destination_details_slug"),
    path("tours/", views.tours, name="tours"),
    path("tours/<slug:slug>/", views.tour_details, name="tour_details_slug"),
    path("tours/<slug:slug>/book/", views.create_tour_booking, name="tour_booking"),
    path("contact/", views.contact, name="contact"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("safety-tips/", views.safety_tips, name="safety_tips"),

    # Authentication
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.SafariLoginView.as_view(), name="login"),
    path("auth/logout/", views.SafariLogoutView.as_view(), name="logout"),

    # User dashboard and profiles
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notifications, name="notifications"),
    path("profile/<str:username>/", views.profile_detail, name="profile_detail"),
    path("profile/<str:username>/edit/", views.profile_update, name="profile_update"),
    path("profile/<str:username>/verify/", views.profile_verify, name="profile_verify"),

    # Ride-sharing
    path("rides/", views.RideListView.as_view(), name="ride_list"),
    path("rides/offer/", views.OfferRideView.as_view(), name="offer_ride"),
    path("rides/my/", views.my_rides, name="my_rides"),
    path("rides/<int:pk>/", views.RideDetailView.as_view(), name="ride_detail"),
    path("rides/<int:pk>/book/", views.book_ride, name="book_ride"),
    path("rides/<int:pk>/message/", views.send_ride_message, name="send_ride_message"),
    path("bookings/my/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:pk>/cancel/", views.cancel_ride_booking, name="cancel_ride_booking"),
    path("vehicles/add/", views.vehicle_create, name="vehicle_create"),

    # Driver and safety
    path("guide/apply/", views.become_guide, name="become_guide"),
    path("sos/", views.sos_alert, name="sos_alert"),

    # Custom admin views
    path("admin/custom/", views.custom_admin_dashboard, name="custom_admin_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/users/", views.admin_users, name="admin_users"),
    path("admin-dashboard/rides/", views.admin_rides, name="admin_rides"),
    path("admin-dashboard/bookings/", views.admin_bookings, name="admin_bookings"),
    path("admin-dashboard/verifications/", views.admin_verifications, name="admin_verifications"),
    path("admin-dashboard/sos-alerts/", views.admin_sos_alerts, name="admin_sos_alerts"),
    path("admin-dashboard/reviews/", views.admin_reviews, name="admin_reviews"),
    path("admin-dashboard/contact-messages/", views.admin_contact_messages, name="admin_contact_messages"),
    path("admin-dashboard/reports/", views.admin_reports, name="admin_reports"),

    # REST-ready API endpoints
    path("api/rides/", views.api_rides, name="api_rides"),
    path("api/rides/<int:pk>/availability/", views.api_ride_availability, name="api_ride_availability"),
    path("api/notifications/unread-count/", views.api_unread_notifications, name="api_unread_notifications"),
]
