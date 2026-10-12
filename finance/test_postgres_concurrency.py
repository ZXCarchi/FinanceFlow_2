"""Exercise real row locks in PostgreSQL CI; SQLite cannot prove this guarantee."""
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.contrib.auth.models import User
from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase

from .models import RecurringOccurrence, RecurringPayment, Transaction, Wallet


@skipUnless(connection.vendor == 'postgresql', 'Requires PostgreSQL row-lock semantics.')
class RecurringConcurrencyTests(TransactionTestCase):
    def test_simultaneous_apply_creates_one_transaction_per_rule(self):
        user = User.objects.create_user('concurrent@example.com', password='Concurrent!934721')
        wallet = Wallet.objects.create(user=user, name='Main')
        # Identical labels and amounts are separate rules, not duplicate receipts.
        for _ in range(2):
            RecurringPayment.objects.create(user=user, wallet=wallet, title='Subscription', amount='10.00', day_of_month=1)

        clients = [Client(), Client()]
        for client in clients:
            client.force_login(user)
        start = Barrier(2, timeout=5)

        def apply(client):
            # Each worker uses its own database connection and authenticated session.
            close_old_connections()
            try:
                with connection.cursor() as cursor:
                    # A broken locking protocol fails promptly instead of hanging CI.
                    cursor.execute("SET lock_timeout = '5s'")
                    cursor.execute("SET statement_timeout = '10s'")
                start.wait()
                response = client.post('/api/recurring/apply', json.dumps({'month': '2024-01'}), content_type='application/json')
                return response.status_code, response.json()
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(apply, client) for client in clients]
            results = [future.result(timeout=20) for future in futures]

        self.assertEqual([status for status, _ in results], [200, 200], results)
        self.assertEqual(sorted(body['created'] for _, body in results), [0, 2])
        self.assertEqual(Transaction.objects.filter(user=user).count(), 2)
        self.assertEqual(RecurringOccurrence.objects.count(), 2)
        self.assertEqual(RecurringOccurrence.objects.values('transaction_id').distinct().count(), 2)
        self.assertFalse(RecurringOccurrence.objects.filter(transaction__isnull=True).exists())
