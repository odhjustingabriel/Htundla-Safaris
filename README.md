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
5. Staff users review/finalize proposals in the dedicated staff portal.
6. Superusers manage staff users and roles in the separate superuser portal.
7. Proposal communication is sent by email (console backend for development by default).

---

## Features
- Existing pages preserved and routed via Django templates:
  - Homepage
  - Destinations
  - Contact Us
- Guided chatbot conversation for inquiry intake
- Rule-based itinerary recommendation engine
- Dedicated staff portal for inquiry review and proposal finalization
- Dedicated superuser portal for staff user and role management
- Styled staff/superuser login pages that match the client-facing site
- Finalization and proposal sending flow
- Chronological itinerary display and emails ordered by Morning, Afternoon, then Evening
- Seed command for destinations and activities

---

## Clone the Repository
```bash
git clone https://github.com/odhjustingabriel/Htundla-Safaris.git
cd Htundla-Safaris
```

---

## Django Environment Setup

### Runtime versions

This project is pinned to a Django 5.2 LTS-compatible runtime:

- Python: `3.12.13` (see `.python-version`)
- Django: `5.2.15` (see `requirements.txt`)

Use Python 3.12 for the local virtual environment. Django 5.2 LTS also supports newer Python releases, but this repository pins Python 3.12.13 for predictable local setup.

### 1) Create and activate virtual environment
**Linux/macOS**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

**With pyenv**
```bash
pyenv install 3.12.13  # if not already installed
pyenv local 3.12.13
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3) Run migrations
```bash
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
- `http://127.0.0.1:8000/staff/login/`
- `http://127.0.0.1:8000/operator/dashboard/` *(staff portal)*
- `http://127.0.0.1:8000/superuser/login/`
- `http://127.0.0.1:8000/superuser/dashboard/` *(superuser portal)*


## Staff and Superuser Portals

The project has two in-app portal entry points in addition to Django's built-in `/admin/`:

| Portal | Login URL | Dashboard URL | Who can access | Purpose |
| --- | --- | --- | --- | --- |
| Staff Portal | `http://127.0.0.1:8000/staff/login/` | `http://127.0.0.1:8000/operator/dashboard/` | Any authenticated user with `is_staff=True`, including superusers | Review customer inquiries, filter records, review generated itineraries, edit drafts, and send proposals. |
| Superuser Portal | `http://127.0.0.1:8000/superuser/login/` | `http://127.0.0.1:8000/superuser/dashboard/` | Authenticated users with `is_superuser=True` | Create/edit staff users and create/edit staff roles/groups. |

The staff and superuser portals intentionally do **not** cross-link to each other in their navigation. Use the correct login URL for the portal you want to access.

### Accessing the Staff Portal
1. Create a staff-capable account if needed. A superuser created with `createsuperuser` can also access the staff portal:
   ```bash
   python manage.py createsuperuser
   ```
2. Start the server:
   ```bash
   python manage.py runserver
   ```
3. Open the staff login page:
   - `http://127.0.0.1:8000/staff/login/`
4. After a successful staff login, Django redirects to:
   - `http://127.0.0.1:8000/operator/dashboard/`

### Accessing the Superuser Portal
1. Create a superuser if needed:
   ```bash
   python manage.py createsuperuser
   ```
2. Open the superuser login page:
   - `http://127.0.0.1:8000/superuser/login/`
3. After a successful superuser login, Django redirects to:
   - `http://127.0.0.1:8000/superuser/dashboard/`

If a non-superuser attempts to sign in through the superuser login page, the page stays open and displays a clear authorization error.


---

## Recent Admin Portal Updates

The current staff/superuser workflow includes these updates:

- Fixed the staff dashboard template syntax issue that previously caused `TemplateSyntaxError` at `/operator/dashboard/`.
- Added polished Create Staff User and Create Staff Role pages with consistent primary/secondary action buttons and less crowded role/permission controls.
- Added dedicated staff and superuser login pages styled with the same visual language as the client-facing site.
- Kept staff and superuser portal navigation separate, while allowing superusers to access the staff portal when they need to review operational inquiries.
- Fixed sticky navbar hover behavior so scrolled navigation links still turn white on hover/focus.
- Ordered draft itinerary items consistently by day and slot: `Morning`, `Afternoon`, then `Evening`.
- Added tests covering portal rendering, login redirects, authorization behavior, and itinerary ordering.

---

## Project Structure (Key Files)
- `htundla_safaris/settings.py` – Django settings
- `htundla_safaris/urls.py` – route configuration
- `core/models.py` – data models
- `core/forms.py` – backend validation
- `core/recommender.py` – rule-based itinerary logic
- `core/views.py` – page, portal login, access-control, proposal, and itinerary workflow views
- `core/admin.py` – Django admin workflow
- `core/management/commands/seed_data.py` – demo dataset seeding
- `core/templates/core/` – homepage, destinations, contact, staff portal, superuser portal, and login templates
- `css/styles.css` – site styling, including sticky navbar hover behavior

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

---

## Security Hardening Features (Implemented)

The application includes the following security controls:

- **Global rate limiting** on all routes through middleware (`core.middleware.SecurityHardeningMiddleware`).
- **Authentication route throttling**: max **5 attempts per 15 minutes** for admin auth endpoints (`/admin/login/`, `/admin/logout/`, `/admin/password_reset/`).
- **Payload validation and abuse prevention**:
  - Reject oversized request bodies using `MAX_PAYLOAD_BYTES`.
  - Reject malformed `CONTENT_LENGTH` values.
  - Restrict mutating request content types to expected types.
- **Server-side input validation**:
  - Inquiry form validation for destination and business rules.
  - Proposal form validation (`final_cost`, `proposal_notes` max length).
- **Access control hardening**:
  - Staff portal routes require `is_staff=True` and redirect unauthenticated users to `/staff/login/`.
  - Superuser management routes require `is_superuser=True` and redirect users to `/superuser/login/`.
  - Superuser credentials are required to manage staff users and roles.
  - Safe `next` redirect validation is used after portal login.
- **Secure runtime configuration**:
  - Secrets/config moved to environment variables (`DJANGO_SECRET_KEY`, etc.).
  - `.env.example` added for required environment settings.
- **Security headers and cookie protections**:
  - `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS='DENY'`, `REFERRER_POLICY='same-origin'`.
  - `SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_HTTPONLY`.
  - `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
  - `SECURE_SSL_REDIRECT` and HSTS options.
- **Credential hygiene**:
  - No hardcoded API keys/tokens/passwords in source; secret scanning performed.
- **Authentication strength**:
  - Django password validators enabled with minimum length and common-password checks.
- Development defaults disable HTTPS redirect, HSTS, secure cookies, and use Django DummyCache to avoid HTTPS/cache side effects while running `runserver`.

### Required Environment Variables


### Local Development HTTPS Note

If you run `python manage.py runserver` locally, Django serves **HTTP only** by default.
If `SECURE_SSL_REDIRECT=True`, requests are redirected to `https://...`, which causes browser/dev-server protocol errors (400 bad request with TLS handshake bytes).

For local development, set:

- `DJANGO_DEBUG=True`
- `SECURE_SSL_REDIRECT=False`

In production, keep `SECURE_SSL_REDIRECT=True` behind a proper TLS-terminating proxy/load balancer.


Use `.env.example` as a baseline:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `RATE_LIMIT_WINDOW_SECONDS`
- `RATE_LIMIT_DEFAULT_REQUESTS`
- `RATE_LIMIT_AUTH_REQUESTS`
- `MAX_PAYLOAD_BYTES`
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`

---

## OWASP Top 10 Countercheck (2021)

This section maps current controls to OWASP Top 10 categories:

1. **A01: Broken Access Control**  
   - Mitigation: staff portal routes require staff accounts, superuser management routes require superuser accounts, and portal login redirects validate `next` URLs before redirecting.

2. **A02: Cryptographic Failures**  
   - Mitigation: secrets removed from source and provided by environment variables; HTTPS redirect and secure cookies enabled for transport/session protection.

3. **A03: Injection**  
   - Mitigation: Django ORM + server-side form validation and constrained payload content types reduce injection risk.

4. **A04: Insecure Design**  
   - Mitigation: defense-in-depth middleware for rate limiting and request-shape validation to reduce abuse patterns.

5. **A05: Security Misconfiguration**  
   - Mitigation: hardened defaults for headers/cookies/HSTS/SSL redirect; explicit environment-based security configuration.

6. **A06: Vulnerable and Outdated Components**  
   - Status: **Operational control required**. Keep Django and dependencies updated with routine patching.

7. **A07: Identification and Authentication Failures**  
   - Mitigation: auth endpoint throttling (5/15min), strong password validation policies, and dedicated portal login forms for staff and superuser access.

8. **A08: Software and Data Integrity Failures**  
   - Status: **Partially addressed**. Recommend adding dependency pinning and CI integrity checks (hash-locked requirements, signed releases where possible).

9. **A09: Security Logging and Monitoring Failures**  
   - Status: **Gap remains**. Recommend structured security logging/alerting for rate-limit blocks, auth failures, and privileged actions.

10. **A10: Server-Side Request Forgery (SSRF)**  
    - Mitigation: no user-driven outbound URL fetch functionality exists in current app flow.

### Remaining Recommended Actions

- Add centralized logging and alerting for suspicious activity (A09).
- Add dependency management policy (pinning + regular updates) (A06/A08).
- In production, set strict hostnames and never run with `DJANGO_DEBUG=True`.


### Important: `.env.example` is not auto-loaded
This project does **not** use `python-dotenv` currently, so values in `.env.example` are only a reference.
Django reads real values from your system environment variables (PowerShell `setx` / `$env:`) or defaults in `settings.py`.


### Runserver HTTPS noise troubleshooting (development)
If you still see logs like **"You're accessing the development server over HTTPS, but it only supports HTTP"**, this is usually client-side (browser/proxy/extension) forcing HTTPS before Django handles the request.

What we changed in code:
- Disabled HTTPS redirect/HSTS defaults in development settings.
- In `DEBUG=True`, removed `SecurityMiddleware` and custom hardening middleware from active middleware chain to avoid any app-level redirect influence.

What to do locally:
- Open exactly `http://127.0.0.1:8000/` (not `https://`).
- Try Incognito/Private window.
- Clear HSTS/HTTPS-only settings for `127.0.0.1` and `localhost` in your browser.
- Disable HTTPS-enforcing extensions/proxy/VPN/antivirus web shield temporarily for localhost testing.
