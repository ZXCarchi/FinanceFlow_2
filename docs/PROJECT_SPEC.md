# Product scope — upgraded version

FinanceFlow is an English personal-finance ledger for individuals. Its core workflows are recording income/expenses, tracking active-account balances, setting personal saving goals, allocating a monthly budget and reviewing category spending.

## Technology

- Frontend: standard JavaScript modules, semantic HTML and shared CSS; interactive SVG charts.
- Backend: Python / Django, JSON API, cookie sessions, server-side validation.
- Database: PostgreSQL; explicit SQLite development fallback only.
- Runtime: single origin; Django/WhiteNoise serves static assets. Docker Compose supports local PostgreSQL + app setup.

## Pages

- Dashboard: current active-account balance, selected-month income/expenses/net, recent entries, goals and spending breakdown.
- Transactions: create/edit/delete, category/type/search filtering, month selection, monthly CSV export.
- Accounts: initial balances, account type, name and archive state. Referenced accounts cannot be destructively deleted.
- Goals: name, target, saved amount and optional date. Progress is manual and independent of ledger movements.
- Planner: editable three-part allocation, income setting and category budgets; percentages sum exactly100.
- Reports: monthly category distribution and six-month income/expense trend.
- Recurring: editable monthly rules, explicit Apply due action and permanent monthly receipts.
- Settings: display name, base currency, expected income and category management.
- Coach: local rules explaining the user's numbers, without external AI calls.

## Design and access

All screens use common components and tokens. Desktop sidebar, tablet adaptation and mobile navigation must retain access to every page. Inputs are labelled, dialogs support keyboard operation, focus is visible, empty states explain the next action, and animations respect reduced-motion preferences.

## Deliberate limits

One base currency per user, no exchange rates or bank sync. No automatic money transfers, payment execution or unattended recurring job. Password recovery/email verification are a separate follow-up that needs configured email delivery. Public launch also needs HTTPS, backups, monitoring and deployment-specific checks.
