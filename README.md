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
- SQLite by default; PostgreSQL via `DATABASE_URL` (Railway-ready)
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

## Deployment Notes (Railway)
Railway deployment is configured in `railway.json`.

- Build command: `python manage.py collectstatic --noinput`
- Pre-deploy command: `python manage.py migrate --noinput`
- Start command: `gunicorn kenya_travel.wsgi:application --bind 0.0.0.0:$PORT --workers=2 --threads=4 --timeout=120`
- `settings.py` auto-adds `RAILWAY_PUBLIC_DOMAIN` and `RAILWAY_PRIVATE_DOMAIN` to `ALLOWED_HOSTS`.
- If you attach a Railway volume, uploaded media will be stored under `$RAILWAY_VOLUME_MOUNT_PATH/media`.

### Deploy on Railway
1. Push this repository to GitHub.
2. In Railway, create a new project and choose **Deploy from GitHub repo**.
3. Add a PostgreSQL service to the Railway project.
4. In the Django app service, add this variable: `DATABASE_URL=${{Postgres.DATABASE_URL}}`.
5. Add required Django/app variables:
   - `DJANGO_SECRET_KEY=<strong secret>`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<your custom domain if any>`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your custom domain>` if you use a custom domain
   - Email, M-Pesa, `OPENWEATHER_API_KEY`, and optional Redis variables as needed
6. Deploy the service. Railway will run `collectstatic`, run migrations, then start Gunicorn on `$PORT`.
7. After deployment, open the app service Settings > Networking and click **Generate Domain**.

### Important Secret Cleanup
`.env` is currently tracked in this repository. Do not push secrets to GitHub or Railway. Keep the local file, but remove it from Git tracking before your next commit:

```bash
git rm --cached .env
git commit -m "Stop tracking local environment file"
```

If this repository has already been pushed publicly, rotate the secrets stored in `.env`.
