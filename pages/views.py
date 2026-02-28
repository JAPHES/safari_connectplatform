from django.shortcuts import render


def home(request):
    return render(request, 'pages/index.html')


def about(request):
    return render(request, 'pages/about.html')


def destinations(request):
    return render(request, 'pages/destinations.html')


def destination_details(request):
    return render(request, 'pages/destination-details.html')


def tours(request):
    return render(request, 'pages/tours.html')


def tour_details(request):
    return render(request, 'pages/tour-details.html')


def gallery(request):
    return render(request, 'pages/gallery.html')


def blog(request):
    return render(request, 'pages/blog.html')


def blog_details(request):
    return render(request, 'pages/blog-details.html')


def booking(request):
    return render(request, 'pages/booking.html')


def testimonials(request):
    return render(request, 'pages/testimonials.html')


def faq(request):
    return render(request, 'pages/faq.html')


def contact(request):
    return render(request, 'pages/contact.html')


def terms(request):
    return render(request, 'pages/terms.html')


def privacy(request):
    return render(request, 'pages/privacy.html')


def starter_page(request):
    return render(request, 'pages/starter-page.html')


def not_found(request):
    return render(request, 'pages/404.html')
