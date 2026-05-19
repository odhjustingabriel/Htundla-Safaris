# Htundla Safaris

A final-year project website for **Htundla Safaris** (Safari + MICE) implemented with a simple KISS architecture:
- Frontend: HTML, CSS, JavaScript
- Backend: Django
- Recommendation: rule-based itinerary generation (no external AI API dependency)

---

## Project Overview
This project turns the existing static website into a Django-powered workflow where:
1. A visitor uses a guided chatbot on the Contact Us page.
2. Preferences are validated on frontend + backend.
3. Inquiry data is stored in the database.
4. A draft itinerary is auto-generated.
5. Operators review/finalize proposals in Django admin.
6. Proposal communication is sent by email (console backend for development by default).

---

## Features
- Existing pages preserved and routed via Django templates:
  - Homepage
  - Destinations
  - Contact Us
- Guided chatbot conversation for inquiry intake
- Rule-based itinerary recommendation engine
- Centralized admin/operator review workflow
- Finalization and proposal sending flow
- Seed command for destinations and activities

---

## Clone the Repository
```bash
git clone https://github.com/odhjustingabriel/Htundla-Safaris.git
cd Htundla-Safaris
```

---

## Django Environment Setup

### 1) Create and activate virtual environment
**Linux/macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
pip install django
```

### 3) Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4) Create admin user
```bash
python manage.py createsuperuser
```

### 5) Seed sample data
```bash
python manage.py seed_data
```

### 6) Start development server
```bash
python manage.py runserver
```

Open in browser:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/destinations/`
- `http://127.0.0.1:8000/contactus/`
- `http://127.0.0.1:8000/admin/`

---

## Project Structure (Key Files)
- `htundla_safaris/settings.py` – Django settings
- `htundla_safaris/urls.py` – route configuration
- `core/models.py` – data models
- `core/forms.py` – backend validation
- `core/recommender.py` – rule-based itinerary logic
- `core/views.py` – page and workflow views
- `core/admin.py` – operator/admin workflow
- `core/management/commands/seed_data.py` – demo dataset seeding
- `core/templates/core/` – homepage, destinations, contact templates
- `css/styles.css` – site styling

---

## Email Configuration
Default development mode uses Django console backend:
- Email content prints in terminal.

To use SMTP later, set in `settings.py`:
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`

---

## Notes
- This is an academic demo-focused system (not enterprise-grade).
- The chatbot is scripted/guided by design.
- Recommendation logic is deterministic and rule-based for explainability.

---

## License (MIT)
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Security & Environment Variables
- Copy `.env.example` to your environment and set production-safe values.
- `DJANGO_SECRET_KEY`, database credentials, and email credentials must be provided via environment variables.
- Global rate limiting and auth route rate limiting are configurable via env vars.
- Request body size is enforced using `MAX_REQUEST_BODY_SIZE`.
