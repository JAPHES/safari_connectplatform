# SafariConnect - Kenya travel & ride-sharing

A Django 6.0 app for planning trips across Kenya: discover destinations, book rides, message drivers, and manage bookings from a unified dashboard.

## Core Features
- Auth flows: register, login, logout, and two-step forgot-password reset (lookup then password update).
- UX polish: aligned forms, password show/hide toggle, reduced signup help text.
- Rides: list rides, view details, book, cancel, and message drivers; ride offering limited to verified drivers.
- Destinations & tours: browse Kenyan towns (Nairobi, Mombasa, Nakuru, Kisumu) with hero/home content and global footer.
- Safety: SOS trigger and accordion-based Safety FAQ.
- Profiles: custom `pages.User` model with avatar upload shown in navbar/dashboard/profile; cache-busted URLs for instant refresh.
- Notifications: in-app messaging, replies, notifications page, unread badge with auto-refresh.
- Admin: custom `/admin-dashboard/` (separate from Django admin) covering users, rides, bookings, verifications, SOS, reviews, contact messages, and reports with filters, actions, and CSV export.

## Stack & Prerequisites
- Python 3.11+ recommended
- Django 6.0, Gunicorn, Whitenoise
- SQLite by default; PostgreSQL via `DATABASE_URL` (Render-ready)
- Optional: Redis for cache/channels/Celery

## Configuration (.env)
Create a `.env` in project root (sample values exist in the checked-in `.env`; do not commit secrets). Key variables:
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL` (set to your Postgres URI; defaults to SQLite if omitted)
- Email: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- M-Pesa (Daraja): `MPESA_ENVIRONMENT`, `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY`, `MPESA_CALLBACK_URL`
- Redis/Celery: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`

## Local Development
1. Create and activate a virtualenv.
2. Install deps: `pip install -r requirements.txt`
3. Apply migrations: `python manage.py migrate`
4. (Optional) Create a superuser for dashboards: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`

Static files: served by Whitenoise in dev; run `python manage.py collectstatic` for production assets.

## Testing
- Run all tests: `python manage.py test`
- Focused app tests: `python manage.py test pages`

## Useful Routes
- Home `/`
- Register `/auth/register/`
- Login `/auth/login/`
- Forgot password `/auth/forgot-password/` then `/auth/forgot-password/reset/`
- Profile edit `/profile/<username>/edit/`
- Rides `/rides/` and bookings `/bookings/my/`
- Safety FAQ `/safety-tips/`
- Notifications `/notifications/`
- Admin dashboard (superuser) `/admin-dashboard/`

## Deployment Notes (Render-friendly)
- Procfile runs: `gunicorn --chdir /opt/render/project/src kenya_travel.wsgi:application --bind=0.0.0.0:10000 --workers=2 --threads=4 --timeout=120`
- Ensure `DJANGO_ALLOWED_HOSTS` includes Render hostname; `settings.py` auto-adds `RENDER_EXTERNAL_HOSTNAME` and `safari-connect.onrender.com`.
- Set `DEBUG=False`, configure `DATABASE_URL`, email, and M-Pesa secrets; add `REDIS_URL` to enable Redis-backed cache/channels.
