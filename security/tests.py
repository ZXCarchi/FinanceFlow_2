"""Regression tests for request-level protections, independent of UI behavior."""
import hashlib
import json
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from .middleware import AuthRateLimitMiddleware, SecurityHeadersMiddleware
from .models import AuthRateBucket


class SecurityHeadersTests(SimpleTestCase):
    def test_personal_api_responses_are_not_cacheable(self):
        request = RequestFactory().get('/api/state')
        response = SecurityHeadersMiddleware(lambda request: HttpResponse('{}'))(request)
        self.assertEqual(response['Cache-Control'], 'no-store, private')
        policy = response['Content-Security-Policy']
        self.assertIn("script-src 'self'", policy)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertIn("form-action 'self'", policy)
        self.assertIn('camera=()', response['Permissions-Policy'])


@override_settings(AUTH_RATE_LIMIT_ENABLED=True)
class AuthRateLimitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AuthRateLimitMiddleware(lambda request: HttpResponse(status=204))
        self.window = 1_800_000_000

    def attempt(self, email='person@example.com', ip='192.0.2.1', forwarded=None, now=None):
        request = self.factory.post(
            '/api/login', data=json.dumps({'email': email, 'password': 'irrelevant'}),
            content_type='application/json', REMOTE_ADDR=ip,
        )
        if forwarded is not None:
            request.META['HTTP_X_FORWARDED_FOR'] = forwarded
        with patch('security.middleware.time.time', return_value=self.window if now is None else now):
            return self.middleware(request)

    def test_account_limit_is_shared_across_peer_addresses(self):
        for index in range(12):
            self.assertEqual(self.attempt(ip=f'192.0.2.{index + 1}').status_code, 204)
        response = self.attempt(email=' PERSON@EXAMPLE.COM ', ip='192.0.2.99')
        self.assertEqual(response.status_code, 429)
        self.assertGreater(int(response['Retry-After']), 0)
        account_key = hashlib.sha256(b'account:person@example.com').hexdigest()
        self.assertEqual(AuthRateBucket.objects.get(key=account_key).count, 13)

    def test_forwarded_header_does_not_bypass_peer_limit(self):
        for index in range(40):
            response = self.attempt(email=f'person{index}@example.com', forwarded=f'198.51.100.{index}')
            self.assertEqual(response.status_code, 204)
        self.assertEqual(self.attempt(email='different@example.com', forwarded='203.0.113.1').status_code, 429)

    def test_next_window_restores_access(self):
        for _ in range(12):
            self.attempt()
        self.assertEqual(self.attempt().status_code, 429)
        self.assertEqual(self.attempt(now=self.window + 900).status_code, 204)
        account_key = hashlib.sha256(b'account:person@example.com').hexdigest()
        self.assertEqual(AuthRateBucket.objects.get(key=account_key).count, 1)

    def test_malformed_json_counts_attempt_without_crashing(self):
        request = self.factory.post('/api/login', data='{broken', content_type='application/json', REMOTE_ADDR='192.0.2.7')
        self.assertEqual(self.middleware(request).status_code, 204)
        self.assertEqual(AuthRateBucket.objects.count(), 1)

    def test_other_requests_do_not_consume_auth_attempts(self):
        for request in [self.factory.get('/api/login'), self.factory.post('/api/transactions')]:
            self.assertEqual(self.middleware(request).status_code, 204)
        self.assertFalse(AuthRateBucket.objects.exists())

    def test_disabled_limiter_does_not_write_buckets(self):
        with override_settings(AUTH_RATE_LIMIT_ENABLED=False):
            self.assertEqual(self.attempt().status_code, 204)
        self.assertFalse(AuthRateBucket.objects.exists())
