# Htundla Safaris (Django Demo)

## Setup
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install django`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `python manage.py seed_data`
6. `python manage.py runserver`

## Pages
- `/` homepage
- `/destinations/`
- `/contactus/` guided chatbot inquiry form
- `/admin/` operator workflow

## Email
Uses console backend by default (`EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend`).
Switch to SMTP by setting `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`.
