# SafariConnect (Kenya Travel + Rides)

A Django web app for Kenya travel planning with destination discovery, tours, and ride-sharing between major towns.

## Features
- User authentication: register, sign in, sign out
- Improved auth UX:
  - Cleaner aligned login form
  - Password show/hide toggle
  - Reduced signup help-text noise (rules shown via validation errors)
- Destination and tour browsing
- Ride listing, ride details, ride booking, and booking cancellation
- Driver tools: offer rides, manage rides, add vehicle
  - Offer ride is restricted to approved drivers only
- Safety tools: SOS and Safety FAQ accordion
- Profile image support:
  - Upload avatar in profile edit
  - Avatar visible in navbar, dashboard, and profile page
  - Cache-busted avatar URLs for immediate refresh after update
- Home page enhancements:
  - Coverage cards for Kenyan towns (Nairobi, Mombasa, Nakuru, Kisumu)
  - Global footer across pages
- Messaging and notifications:
  - Driver/passenger ride messaging with reply support
  - Notifications page for received messages
  - Dashboard preview of unread messages
  - Live top-bar bell badge auto-refresh (unread count)
- Superuser admin dashboard:
  - Custom `/admin-dashboard/` area (separate from Django admin)
  - Users, rides, bookings, verifications, SOS, reviews, contact messages, reports
  - Action buttons, filters, charts, and CSV exports

## Project Structure
- `kenya_travel/`: Django project settings and root URL config
- `pages/`: app models, views, forms, URLs, and tests
- `templates/pages/`: app templates (including auth pages)
- `static/assets/`: CSS, JS, images, and vendor libraries
- `requirements.txt`: project dependencies

## Run Locally
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Apply database migrations:
   `python manage.py migrate`
4. Start development server:
   `python manage.py runserver`

## Useful Routes
- Home: `/`
- Register: `/auth/register/`
- Login: `/auth/login/`
- Profile edit: `/profile/<username>/edit/`
- Rides: `/rides/`
- My bookings: `/bookings/my/`
- Safety FAQ: `/safety-tips/`
- Notifications: `/notifications/`
- Admin dashboard (superuser only): `/admin-dashboard/`

## Recent Implementation Notes
- Logout now uses secure POST forms (compatible with Django 5.2 `LogoutView`).
- Ride booking validation fixed to prevent `RideBooking has no ride` during form validation.
- Username rules were relaxed and signup help-text noise reduced.
  - New migration added: `pages/migrations/0002_alter_user_username.py`
- Custom superuser admin dashboard implemented with section-specific management pages.
- Ride offering now requires approved driver verification.
- In-app message notifications, reply flow, and unread badge polling are active.
