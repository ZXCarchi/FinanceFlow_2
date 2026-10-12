# Verification — 11 October 2026

- 37 Django tests passed on the explicitly enabled local SQLite test database: financial calculations, API validation, ownership, CSRF, CSV escaping, recurring application and authentication throttling.
- An additional PostgreSQL-only concurrency test was discovered and correctly skipped locally. A PostgreSQL 17 CI workflow is included; it has not been run on GitHub.
- Migrations applied successfully to a fresh local development database; no missing migrations detected.
- Production configuration checks completed without warnings. Static asset collection and JavaScript syntax checks passed.
- Browser checks: demo login, invalid percentage total, saving 60/25/15 and persistence after reload, adding a 12.34 PLN expense and updated balance/spending, empty-month reports, all nine pages, and local coach response matching the saved plan.
- Layout inspected at 390×844, 768×1024 and 1440×900; no horizontal page overflow in inspected views. Mobile menu and transaction dialog checked. No browser JavaScript errors found during these checks.

## Verification limits

Real PostgreSQL and Docker execution were unavailable in this environment. PostgreSQL startup was blocked by the environment's shared-memory restrictions. Production deployment, existing user-data migration and the PostgreSQL concurrency test therefore remain to be verified on the target host. No public site or GitHub repository has been updated.

The ZIP excludes local demo data, Python virtual environments, caches, collected static output and secrets. Docker/start scripts install dependencies and generate required runtime files.
