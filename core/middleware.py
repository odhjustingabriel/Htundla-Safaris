import time
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


class RateLimitMiddleware:
    """Simple per-IP rate limiting middleware.

    - Applies a global rate limit to all endpoints.
    - Applies stricter limits to authentication routes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = self._client_ip(request)
        path = request.path or "/"

        if self._is_rate_limited(client_ip, path):
            return HttpResponse("Too many requests. Please try again later.", status=429)

        return self.get_response(request)

    def _is_rate_limited(self, ip, path):
        now = int(time.time())

        if self._is_auth_route(path):
            window = getattr(settings, "AUTH_RATE_LIMIT_WINDOW_SECONDS", 900)
            max_requests = getattr(settings, "AUTH_RATE_LIMIT_MAX_REQUESTS", 5)
            key = f"rl:auth:{ip}:{now // window}"
            current = cache.get(key, 0)
            if current >= max_requests:
                return True
            cache.set(key, current + 1, timeout=window)
            return False

        window = getattr(settings, "GLOBAL_RATE_LIMIT_WINDOW_SECONDS", 60)
        max_requests = getattr(settings, "GLOBAL_RATE_LIMIT_MAX_REQUESTS", 120)
        key = f"rl:global:{ip}:{now // window}"
        current = cache.get(key, 0)
        if current >= max_requests:
            return True
        cache.set(key, current + 1, timeout=window)
        return False

    @staticmethod
    def _is_auth_route(path):
        auth_prefixes = (
            "/admin/login",
            "/accounts/login",
            "/accounts/signup",
            "/login",
            "/signup",
            "/api/auth/",
        )
        return any(path.startswith(prefix) for prefix in auth_prefixes)

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RequestSafetyMiddleware:
    """Reject oversized payloads and clearly malformed content length headers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.META.get("CONTENT_LENGTH", "0")
            try:
                size = int(content_length)
            except (TypeError, ValueError):
                return HttpResponse("Malformed payload.", status=400)

            if size < 0:
                return HttpResponse("Malformed payload.", status=400)

            max_size = getattr(settings, "MAX_REQUEST_BODY_SIZE", 1024 * 1024)
            if size > max_size:
                return HttpResponse("Payload too large.", status=413)

        return self.get_response(request)
