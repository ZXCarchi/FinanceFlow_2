import hashlib
import json
import time
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from .models import AuthRateBucket

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, private'
        return response

class AuthRateLimitMiddleware:
    """Shared database counters; PostgreSQL row locks protect multiple workers.

    Peer address is deliberate: do not trust client-supplied forwarding headers.
    A reverse proxy should additionally apply per-client limits at its edge.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (settings.AUTH_RATE_LIMIT_ENABLED and request.method == 'POST'
                and request.path.rstrip('/') in {'/api/login', '/api/register', '/admin/login'}):
            window = int(time.time()) // 900
            buckets = [('ip:' + request.META.get('REMOTE_ADDR', 'unknown'), 40)]
            if request.path.startswith('/api/'):
                try:
                    payload = json.loads(request.body)
                    email = str(payload.get('email', '')).strip().lower() if isinstance(payload, dict) else ''
                except (ValueError, UnicodeDecodeError):
                    email = ''
                if email:
                    buckets.append(('account:' + email[:254], 12))
            for value, limit in buckets:
                key = hashlib.sha256(value.encode()).hexdigest()
                with transaction.atomic():
                    AuthRateBucket.objects.get_or_create(key=key, defaults={'window': window})
                    bucket = AuthRateBucket.objects.select_for_update().get(key=key)
                    if bucket.window != window:
                        bucket.window, bucket.count = window, 0
                    bucket.count += 1
                    bucket.save(update_fields=['window', 'count'])
                    blocked = bucket.count > limit
                if blocked:
                    response = JsonResponse({'error': 'Too many attempts. Please try again in 15 minutes.'}, status=429)
                    response['Retry-After'] = str(900 - int(time.time()) % 900)
                    return response
            AuthRateBucket.objects.filter(window__lt=window - 96).delete()
        return self.get_response(request)
