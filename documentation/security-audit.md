# Security Audit Report

Date: 2026-05-19

## Scope
- Django settings, routes, views, forms, models, and static assets.
- Secret scanning for hardcoded API keys/tokens/password-like values.

## Implemented Security Improvements
1. **Environment variable migration**
   - Moved sensitive/configurable settings to env vars: secret key, debug, allowed hosts, DB credentials, email credentials, rate limits, payload size.
2. **Rate limiting**
   - Added global per-IP rate limiting middleware for all routes.
   - Added strict auth-route limit: **max 5 requests / 15 minutes**.
3. **Payload hardening**
   - Added request safety middleware to reject malformed/negative `CONTENT_LENGTH` and oversized payloads (`413`).
4. **Input sanitization**
   - Added trimming and HTML tag stripping for key inputs.
   - Added stricter checks for name, email normalization/validation, phone length, and interest payload integrity.
5. **Security headers/settings**
   - Enabled secure defaults such as content-type sniffing protection, clickjacking protection, secure cookies in non-debug mode, and SSL redirect option.
6. **Password policy**
   - Enabled Django password validators.

## Secret Scan Results
- Automated grep-style scan across codebase found one hardcoded secret previously (`SECRET_KEY` in settings), now replaced by env var usage.
- No API keys/tokens/passwords found in frontend source files (`js/`, `css/`, templates) during string-pattern scan.

## Remaining Vulnerabilities / Risks
1. **Rate limiting storage backend**
   - Current limiter uses in-memory local cache. In multi-instance production this is not shared and can be bypassed across nodes.
   - Recommendation: Redis-backed cache and atomic increment operations.
2. **Admin endpoint exposure**
   - `/admin/` remains internet-reachable unless infrastructure/network restricts it.
   - Recommendation: IP allowlists, VPN, SSO, and stronger admin hardening.
3. **No explicit per-view authorization decorator on proposal send endpoint**
   - `send_proposal` should enforce staff/operator permissions at view level, not just rely on workflow assumptions.
4. **No automated security tests yet**
   - Missing tests for rate-limit behavior, malformed payload rejection, and auth protections.
5. **Potential email abuse vector**
   - If proposal-send endpoint access is widened later, outbound email can be abused without additional authorization and anti-automation protections.
6. **No CSP configured**
   - Content Security Policy is not yet defined. Recommendation: add strict CSP for templates and static assets.
7. **No centralized input schema for APIs**
   - If API endpoints are added later, enforce schema validation and stricter body parsing.

## Verification Commands Used
- `rg -n "(AKIA|AIza|xox[baprs]-|ghp_|github_pat_|-----BEGIN|secret|password\s*=|api[_-]?key|token\s*=)" -S --glob '!*.png' --glob '!*.jpg' --glob '!*.jpeg' --glob '!*.drawio*'`
- `python manage.py check`
