# Migrating an existing FinanceFlow database

Keep an untouched backup before importing any real data. Test migration on a copy first. Existing initial migrations and model identifiers are preserved; the new migrations add editable plan fields, validators/constraints, security counters and recurring receipts.

## SQLite to PostgreSQL

1. Stop writes to the old application and back up `db.sqlite3`.
2. In the old application environment, export the domain data and users:

```sh
python manage.py dumpdata auth.User accounts finance --natural-foreign --natural-primary --indent 2 > financeflow-data.json
```

3. Review data on a copy. New validation rejects invalid amounts, category-kind mismatches, bad days, and invalid budgets. Correct invalid records deliberately before importing. Do not silently drop them.
4. Configure the upgraded application to point at an empty PostgreSQL database.
5. Apply migrations and import:

```sh
python manage.py migrate
python manage.py loaddata financeflow-data.json
```

6. Compare user counts, wallet opening balances, all transactions and monthly totals with the backup. Reconcile future-dated transactions: they now do not affect today's balance. Users must sign in again; sessions are not migrated.

For an existing PostgreSQL database, take a backup and run `python manage.py migrate` in the updated code environment. Constraints will correctly stop migration if incompatible old data exists; inspect and repair the copy before repeating on production.

## Recurring payment transition

The old app deduplicated by title, amount, wallet and date. The new app stores explicit item/month receipts. Historical manual or legacy-generated transactions cannot reliably be matched to a recurring item automatically. Review current-month legacy recurring transactions before the first Apply due: pause already-paid recurring items for that month or create the appropriate receipts through an reviewed data migration. Do not click Apply due blindly on imported data.

## Deployment boundary

This deliverable is a local source upgrade. No existing remote database has been migrated, no GitHub commit has been pushed, and no public domain has been deployed.
