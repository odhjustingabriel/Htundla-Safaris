import hashlib
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest


class SecurityHardeningMiddleware:
    """Applies payload checks and coarse rate limiting."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.window = int(getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 900))
        self.default_limit = int(getattr(settings, 'RATE_LIMIT_DEFAULT_REQUESTS', 120))
        self.auth_limit = int(getattr(settings, 'RATE_LIMIT_AUTH_REQUESTS', 5))
        self.max_payload = int(getattr(settings, 'MAX_PAYLOAD_BYTES', 1024 * 1024))

    def __call__(self, request):
        payload_response = self._validate_payload(request)
        if payload_response:
            return payload_response

        limit = self.auth_limit if self._is_auth_route(request.path) else self.default_limit
        if self._is_rate_limited(request, limit):
            return HttpResponse('Rate limit exceeded. Try again later.', status=429)

        return self.get_response(request)

    def _is_auth_route(self, path: str) -> bool:
        auth_prefixes = ['/admin/login/', '/admin/logout/', '/admin/password_reset/']
        return any(path.startswith(prefix) for prefix in auth_prefixes)

    def _client_key(self, request) -> str:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', 'unknown')
        path_hash = hashlib.sha256(request.path.encode('utf-8')).hexdigest()[:16]
        return f'rl:{ip}:{path_hash}'

    def _is_rate_limited(self, request, limit: int) -> bool:
        key = self._client_key(request)
        count = cache.get(key, 0)
        if count >= limit:
            return True
        if count == 0:
            cache.set(key, 1, timeout=self.window)
        else:
            cache.incr(key)
        return False

    def _validate_payload(self, request):
        if request.method not in {'POST', 'PUT', 'PATCH'}:
            return None

        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > self.max_payload:
                    return HttpResponseBadRequest('Payload too large.')
            except ValueError:
                return HttpResponseBadRequest('Malformed content length.')

        allowed_types = {'application/x-www-form-urlencoded', 'multipart/form-data', 'application/json'}
        content_type = (request.content_type or '').split(';')[0].strip()
        if content_type and content_type not in allowed_types:
            return HttpResponseBadRequest('Unsupported content type.')

        return None
