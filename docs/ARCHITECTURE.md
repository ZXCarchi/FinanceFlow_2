# Architecture

```text
Browser
  JavaScript SPA / static/app/
  Shared CSS + inline SVG charts
       | same-origin JSON, session cookie, X-CSRFToken
       v
Python / Django
  finance/api.py       validated user-scoped API
  finance/services.py  Decimal-based calculations
  security/            security headers + shared auth throttles
       | ORM and transactions
       v
PostgreSQL
  profiles, wallets, categories, transactions, goals,
  category limits, recurring items and unique monthly receipts
```

Django serves the SPA shell (`templates/spa.html`) and static files. The browser owns rendering, page state, dialogs and chart previews. The Python API is the source of truth for persisted amounts and calculations. Browser previews are confirmed by fresh server state after saving.

All mutations use JSON, session authentication and CSRF validation. Foreign keys must belong to the authenticated user. API responses are marked no-store. Passwords use Django hashing; browser storage does not hold auth tokens. CSP blocks third-party scripts and inline script execution; inline styles remain allowed for chart dimensions and CSS variables.

Old server-rendered views/templates remain in the source for migration reference but are not mounted by the current router. Only the new SPA, API and admin are reachable. PostgreSQL is the default database; SQLite requires an explicit local-only flag.

Frontend dependencies are deliberately minimal. Figma is optional design tooling, not a runtime service. No external analytics, bank service or AI provider is connected.
