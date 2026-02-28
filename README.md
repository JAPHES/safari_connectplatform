# Safari Kenya Django Project

A Django-based travel website focused on destinations and tours across Kenya.

## Project Structure
- `kenya_travel/` Django project settings and root URLs
- `pages/` app with route views
- `templates/pages/` HTML templates
- `static/assets/` CSS, JS, images, and vendor libraries
- `requirements.txt` Python dependencies

## Run Locally
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run migrations:
   `python manage.py migrate`
4. Start the server:
   `python manage.py runserver`

Main pages:
- Home: `/`
- Destinations: `/destinations/`
- Tours: `/tours/`
- Contact: `/contact/`

## Notes
All templates are in English and branded for Kenya travel content.
