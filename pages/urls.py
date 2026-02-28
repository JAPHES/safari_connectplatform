from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('destinations/', views.destinations, name='destinations'),
    path('destinations/details/', views.destination_details, name='destination_details'),
    path('tours/', views.tours, name='tours'),
    path('tours/details/', views.tour_details, name='tour_details'),
    path('gallery/', views.gallery, name='gallery'),
    path('blog/', views.blog, name='blog'),
    path('blog/details/', views.blog_details, name='blog_details'),
    path('booking/', views.booking, name='booking'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('starter/', views.starter_page, name='starter_page'),
    path('404/', views.not_found, name='not_found'),
]
