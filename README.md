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
  - Proposal-sending workflow restricted to staff users (`@staff_member_required`).
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
   - Mitigation: `send_proposal` route is staff-only (`@staff_member_required`).

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
   - Mitigation: auth endpoint throttling (5/15min) and strong password validation policies.

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
