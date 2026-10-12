# FinanceFlow

A personal finance app with an **English JavaScript interface**, **Python / Django API**, and **PostgreSQL**. This upgrade is based on the supplied FinanceFlow archive (`484b90f9627a40a1136e5e4852851bcdb6ec0579`). The frontend is plain JavaScript modules, HTML and CSS: no Node build step, CDN or separate frontend server is needed.

## Start with Docker (recommended)

Install Docker Desktop (or Docker Engine + Compose), then from this folder:

```sh
cp .env.example .env
```

Set `POSTGRES_PASSWORD` to a strong local password in `.env`. For a local demo keep `DJANGO_DEBUG=1`. Then:

```sh
docker compose up --build
```

Open **http://localhost:8000** and create an account. PostgreSQL data lives in a named volume and survives container restarts. The database port is not exposed publicly. The web port is bound only to this machine.

Optional demo data, for local development only:

```sh
docker compose exec web python manage.py seed_demo
```

Sign in with `demo@financeflow.local` / `DemoPass123!`. This command replaces the demo account's data; never run it against a public deployment.

## Start with local Python + PostgreSQL

Use Python 3.11+ and PostgreSQL 14+. Create a PostgreSQL database and role, copy `.env.example` to `.env`, and set database connection values. Alternatively set `DATABASE_URL` (URL-encode special characters in credentials).

macOS / Linux:

```sh
./start.sh
```

Windows:

```bat
.\start-windows.bat
```

The scripts install dependencies, apply migrations, and run the local development server. They require PostgreSQL to be running. Do not use the development server as a public web server.

For an explicitly opted-in local smoke test without PostgreSQL, set `DJANGO_DEBUG=1` and `FINANCEFLOW_SQLITE_DEV=1`. This fallback is forbidden with production settings; PostgreSQL remains the default.

## Features

- Registration, sign-in and sign-out with server-side sessions.
- Consistent navigation, buttons, cards, forms and dialogs across all pages.
- Dashboard, transactions, wallets, goals, budget planner, reports, recurring payments and settings.
- Create, edit and delete financial records; user-specific categories and category budgets.
- Editable budget percentages with an exact 100% total and a live allocation preview.
- Currency amounts validated and calculated on the server using decimal arithmetic.
- Monthly totals, category breakdown, six-month trend and filtered CSV export.
- Database-protected recurring payment application to prevent duplicate monthly entries.
- Responsive layouts, keyboard-accessible dialogs and reduced-motion support.

## What the numbers mean

- Wallet balance is the opening balance plus recorded income minus expenses dated through today. Future-dated entries do not change today's balance.
- The month selector filters the month's ledger and reports. An entered future-dated transaction can appear in its selected month's report.
- Planned allocation is a target. It does not transfer money or automatically create transactions.
- Goal progress is entered manually and does not move money between wallets.
- Currency is a base/display setting. Changing it does not perform foreign exchange conversion.
- Recurring payments are applied when the user clicks Apply due. There is no background scheduler or bank connection.
- The coach uses local budgeting rules and the user's own data; it is not a generative AI service.

## Tests

With a configured PostgreSQL instance (the test role needs permission to create a test database):

```sh
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py check
```

## Public deployment

Use an HTTPS reverse proxy and Gunicorn. Set `DJANGO_DEBUG=0`, a unique random `DJANGO_SECRET_KEY` of at least 50 characters, exact `DJANGO_ALLOWED_HOSTS`, and HTTPS `DJANGO_CSRF_TRUSTED_ORIGINS`. Set `DJANGO_TRUST_PROXY=1` only if the proxy strips and sets `X-Forwarded-Proto` correctly. Secure cookies, HTTPS redirects and HSTS activate with DEBUG off.

Use PostgreSQL backups, a restricted database account, monitoring, and an edge rate limiter. The app also limits auth requests using shared database counters: 12 per account and 40 per peer IP in a 15-minute window. Behind a reverse proxy, the peer-IP bucket is shared by proxy traffic; tune this policy before a larger launch and retain an edge per-client limiter. Update dependencies regularly.

```sh
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
gunicorn financeflow.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

Deployment hardening follows Django's [deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/). No live GitHub repository or hosted application has been changed by this deliverable.

See [API contract](docs/API.md), [architecture](docs/ARCHITECTURE.md), [migration notes](docs/MIGRATION.md), and [project review](docs/PROJECT_REVIEW_RU.md).
