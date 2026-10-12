/* FinanceFlow: a dependency-free, same-origin application. */
const app = document.querySelector("#app");
const dialog = document.querySelector("#app-dialog");
const toastRegion = document.querySelector("#toast-region");
const routes = [
  "dashboard",
  "transactions",
  "wallets",
  "goals",
  "planner",
  "reports",
  "recurring",
  "coach",
  "settings",
];
const labelsByLocale = {
  en: {
  dashboard: "Overview",
  transactions: "Transactions",
  wallets: "Wallets",
  goals: "Savings goals",
  planner: "Budget planner",
  reports: "Reports",
  recurring: "Recurring payments",
  coach: "Money insights",
  settings: "Settings",
  },
  pl: {
    dashboard: "Przegląd",
    transactions: "Transakcje",
    wallets: "Portfele",
    goals: "Cele oszczędnościowe",
    planner: "Plan budżetu",
    reports: "Raporty",
    recurring: "Płatności cykliczne",
    coach: "Wskazówki finansowe",
    settings: "Ustawienia",
  },
};
const routeIcons = {
  dashboard: "grid",
  transactions: "arrows",
  wallets: "wallet",
  goals: "target",
  planner: "pie",
  reports: "chart",
  recurring: "repeat",
  coach: "sparkles",
  settings: "settings",
};
const colors = [
  "#4b7150",
  "#b9d48f",
  "#a49acb",
  "#e5be85",
  "#96b4a4",
  "#c7cdbe",
];
const icons = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  arrows: '<path d="M4 7h15m-4-4 4 4-4 4M20 17H5m4-4-4 4 4 4"/>',
  wallet:
    '<path d="M20 8V5a2 2 0 0 0-2-2H6a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h14V8H6a2 2 0 0 1 0-4"/><path d="M20 12h-5v5h5"/><path d="M17 14.5h.01"/>',
  target:
    '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  pie: '<path d="M21 13A9 9 0 1 1 11 3v10z"/><path d="M15 3.5A8 8 0 0 1 20.5 9H15z"/>',
  chart: '<path d="M4 3v17h17M8 15V9m5 6V5m5 10v-5"/>',
  repeat:
    '<path d="m17 2 4 4-4 4M3 11V8a2 2 0 0 1 2-2h16M7 22l-4-4 4-4m14-1v3a2 2 0 0 1-2 2H3"/>',
  settings:
    '<path d="m9.5 3-.6 2.1-2 .9-2-.6-2.4 4.2L4 11v2l-1.5 1.4 2.4 4.2 2-.6 2 .9.6 2.1h5l.6-2.1 2-.9 2 .6 2.4-4.2L20 13v-2l1.5-1.4-2.4-4.2-2 .6-2-.9L14.5 3z"/><circle cx="12" cy="12" r="3"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  down: '<path d="M12 4v16m-6-6 6 6 6-6"/>',
  up: '<path d="M12 20V4m-6 6 6-6 6 6"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  back: '<path d="M20 12H4m6-6-6 6 6 6"/>',
  calendar:
    '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18m-13 4h.01M12 15h.01M16 15h.01"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  logout: '<path d="M9 4H4v16h5m-1-8h13m-5-5 5 5-5 5"/>',
  edit: '<path d="m15 4 5 5M4 20l5-1L21 7a2.1 2.1 0 0 0-4-4L5 15z"/>',
  trash: '<path d="M3 6h18M9 6V3h6v3m-10 0 1 15h12l1-15M10 10v7m4-7v7"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  shield:
    '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z"/><path d="m8 12 3 3 5-6"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 4v3"/>',
  leaf: '<path d="M20 3C7 2 1 7 5 15s16 3 15-12Z"/><path d="M4 21 15 10m-7 6 1-7m-1 7 7-1"/>',
  sparkles:
    '<path d="m12 3 2.2 6.8L21 12l-6.8 2.2L12 21l-2.2-6.8L3 12l6.8-2.2L12 3Zm7-1v4m-2-2h4"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  card: '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="M2 9h20M6 15h3"/>',
  cash: '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 12h.01M18 12h.01"/>',
  home: '<path d="m3 10 9-7 9 7v11H3zM9 21v-8h6v8"/>',
  bag: '<path d="M5 7h14l1 14H4L5 7Z"/><path d="M8 7V5a4 4 0 0 1 8 0v2"/>',
  coffee:
    '<path d="M3 7h13v9a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5V7ZM16 8h2a3 3 0 0 1 0 6h-2M6 2v2m4-2v2m4-2v2"/>',
  briefcase:
    '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V3h8v4M3 12h18m-11 0v3h4v-3"/>',
  tag: '<path d="M3 3h8l10 10-8 8L3 11z"/><circle cx="7" cy="7" r="1"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
  plane: '<path d="m22 2-7 20-4-9-9-4 20-7ZM11 13l6-6"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
  heart:
    '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
  pause: '<path d="M8 4v16M16 4v16"/>',
};
const icon = (name, className = "") =>
  `<svg class="icon ${className}" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.tag}</svg>`;
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const parseDecimal = (value) => {
  if (typeof value === "number") return Number.isFinite(value) ? value : NaN;
  const normalized = String(value ?? "")
    .trim()
    .replace(/\s/g, "")
    // Accept comma plus Arabic/full-width decimal separators used by phone keyboards.
    .replace(/[,٫،，]/g, ".");
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(normalized)) return NaN;
  return Number(normalized);
};
const normalizeDecimal = (value) => {
  const parsed = parseDecimal(value);
  return Number.isFinite(parsed) ? String(parsed) : value;
};
const num = (value) => {
  const parsed = parseDecimal(value);
  return Number.isFinite(parsed) ? parsed : 0;
};
const today = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
const state = {
  session: null,
  data: null,
  route: "dashboard",
  month: today().slice(0, 7),
  filters: { search: "", kind: "all", wallet: "all" },
  authMode: location.pathname.includes("signup") ? "signup" : "login",
  loading: false,
  requestId: 0,
  coachMessages: [],
  dialogReturn: null,
  locale: ["pl", "ru"].includes(localStorage.getItem("financeflow-language")) ? "pl" : "en",
};
const labels = new Proxy({}, { get: (_target, key) => labelsByLocale[state.locale][key] });
const localeTag = () => (state.locale === "pl" ? "pl-PL" : "en-GB");
const plText = {
  "YOUR WORKSPACE": "TWOJA PRZESTRZEŃ", MORE: "WIĘCEJ", Workspace: "Przestrzeń",
  "Personal workspace": "Przestrzeń osobista", "Your account": "Twoje konto",
  "Sign out": "Wyloguj się", "Account settings": "Ustawienia konta",
  "A little progress, every day.": "Mały postęp każdego dnia.",
  "Small money habits.": "Dobre nawyki finansowe.",
  "A more confident you.": "Więcej pewności siebie.",
  "Your space. Your numbers. Your next move.": "Twoja przestrzeń. Twoje liczby. Twój następny krok.",
  "Add transaction": "Dodaj transakcję", "Total balance": "Saldo całkowite",
  "Money in": "Wpływy", "Money out": "Wydatki", "Savings rate": "Stopa oszczędności",
  "Cash flow": "Przepływ pieniędzy", Income: "Dochody", Expenses: "Wydatki",
  "Where your money goes": "Na co wydajesz", Details: "Szczegóły",
  "Recent transactions": "Ostatnie transakcje", "View all": "Zobacz wszystkie",
  Transactions: "Transakcje", Wallets: "Portfele", "Savings goals": "Cele oszczędnościowe",
  "Budget planner": "Plan budżetu", Reports: "Raporty", "Recurring payments": "Płatności cykliczne",
  Settings: "Ustawienia", "Money insights": "Wskazówki finansowe",
  "Create account": "Utwórz konto", "Sign in": "Zaloguj się", "Welcome back.": "Witaj ponownie.",
  "Email address": "Adres e-mail", Password: "Hasło", "First name": "Imię",
  "Confirm password": "Potwierdź hasło", "Expected monthly income": "Oczekiwany miesięczny dochód",
  "Display currency": "Waluta", "Save preferences": "Zapisz ustawienia",
  Essentials: "Podstawowe wydatki", Lifestyle: "Wydatki osobiste", Savings: "Oszczędności",
  "Total allocation": "Łączny podział", "Save allocation": "Zapisz podział",
  Reset: "Resetuj", Update: "Aktualizuj", Edit: "Edytuj", Delete: "Usuń",
  Cancel: "Anuluj", "Save changes": "Zapisz zmiany", Create: "Utwórz",
  "Add a transaction": "Dodaj transakcję", "Transaction type": "Typ transakcji",
  Amount: "Kwota", Description: "Opis", Wallet: "Portfel", Category: "Kategoria",
  Date: "Data", "No category": "Bez kategorii", Expense: "Wydatek", Active: "Aktywna",
  Paused: "Wstrzymana", "Opening balance": "Saldo początkowe", "Wallet name": "Nazwa portfela",
  "Target date (optional)": "Data celu (opcjonalna)", "Already saved": "Już odłożono",
  Language: "Język", English: "English", Polish: "Polski",
};
function translateDOM(root) {
  document.documentElement.lang = state.locale;
  if (state.locale !== "pl") return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const raw = node.nodeValue, trimmed = raw.trim(), translated = plText[trimmed];
    if (translated) node.nodeValue = raw.replace(trimmed, translated);
  }
  root.querySelectorAll("[placeholder],[aria-label],[title]").forEach((element) => {
    for (const attr of ["placeholder", "aria-label", "title"]) {
      const value = element.getAttribute(attr);
      if (value && plText[value]) element.setAttribute(attr, plText[value]);
    }
  });
}
const money = (value, options = {}) =>
  new Intl.NumberFormat(localeTag(), {
    style: "currency",
    currency: state.data?.profile?.currency || "PLN",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...options,
  }).format(num(value));
const plainMoney = (value) =>
  new Intl.NumberFormat(localeTag(), {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num(value));
const compactMoney = (value) =>
  new Intl.NumberFormat(localeTag(), {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(num(value));
const monthLabel = (value) =>
  new Date(`${value}-02T12:00:00`).toLocaleDateString(localeTag(), {
    month: "long",
    year: "numeric",
  });
const dateLabel = (value) =>
  value
    ? new Date(`${String(value).slice(0, 10)}T12:00:00`).toLocaleDateString(
        localeTag(),
        { day: "numeric", month: "short", year: "numeric" },
      )
    : "No deadline";
const shortDate = (value) =>
  value
    ? new Date(`${String(value).slice(0, 10)}T12:00:00`).toLocaleDateString(
        localeTag(),
        { day: "numeric", month: "short" },
      )
    : "—";
const initials = () =>
  String(state.session?.user?.first_name || state.session?.user?.email || "You")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((n) => n[0])
    .join("")
    .toUpperCase();
const firstName = () => state.session?.user?.first_name || "there";
const findItem = (collection, id) =>
  state.data?.[collection]?.find((item) => String(item.id) === String(id));
const categoryName = (id) =>
  findItem("categories", id)?.name || "Uncategorized";
const walletName = (id) => findItem("wallets", id)?.name || "Wallet";
const categoryIcon = (id) => {
  const c = findItem("categories", id);
  const name = String(c?.code || c?.name || "").toLowerCase();
  if (/food|grocer|shop/.test(name)) return "bag";
  if (/salary|work|income/.test(name)) return "briefcase";
  if (/hous|rent|home|utilit/.test(name)) return "home";
  if (/transport|travel/.test(name)) return "plane";
  if (/health/.test(name)) return "heart";
  if (/coffee|dining|restaurant/.test(name)) return "coffee";
  return "tag";
};
const button = (
  text,
  action,
  ico = "plus",
  klass = "btn-primary",
  attrs = "",
) =>
  `<button type="button" class="btn ${klass}" data-action="${action}" ${attrs}>${ico ? icon(ico, "small") : ""}${esc(text)}</button>`;
const routeLink = (text, route, ico = "arrow") =>
  `<a href="/${route === "dashboard" ? "" : route + "/"}" data-route="${route}" class="text-btn">${esc(text)}${icon(ico, "small")}</a>`;
const errorText = (err) =>
  err?.message || "Something went wrong. Please try again.";
function toast(message, error = false) {
  const el = document.createElement("div");
  el.className = `toast${error ? " error" : ""}`;
  el.innerHTML = `${icon(error ? "info" : "check")}<span>${esc(message)}</span>`;
  toastRegion.append(el);
  setTimeout(() => el.remove(), 5200);
}
async function api(path, options = {}) {
  const headers = { Accept: "application/json", ...options.headers };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.method && options.method !== "GET")
    headers["X-CSRFToken"] = state.session?.csrfToken || "";
  let response;
  try {
    response = await fetch(`/api/${path.replace(/^\//, "")}`, {
      credentials: "same-origin",
      ...options,
      headers,
      body:
        options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error("Unable to connect. Check your connection and try again.");
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(
      "The server could not complete this request. Please try again.",
    );
  }
  if (!response.ok) {
    if (response.status === 401 && state.session?.authenticated) {
      state.session.authenticated = false;
      state.data = null;
      renderAuth();
    }
    const err = new Error(
      body.error ||
        body.message ||
        "Please check your information and try again.",
    );
    err.fields = body.errors || {};
    err.status = response.status;
    throw err;
  }
  return body;
}
function fieldErrors(form, err) {
  const box = form.querySelector(".form-error");
  if (!box) {
    toast(errorText(err), true);
    return;
  }
  const values = Object.entries(err.fields || {}).flatMap(([field, messages]) =>
    (Array.isArray(messages) ? messages : [messages]).map(
      (message) =>
        `${field === "__all__" || field === "non_field_errors" ? "" : field.replaceAll("_", " ") + ": "}${message}`,
    ),
  );
  box.innerHTML = values.length
    ? `<ul class="error-list">${values.map((v) => `<li>${esc(v)}</li>`).join("")}</ul>`
    : esc(errorText(err));
  box.setAttribute("tabindex", "-1");
  box.focus();
}
async function loadState({ quiet = false } = {}) {
  const requestId = ++state.requestId;
  if (!quiet) {
    state.loading = true;
    document.body.insertAdjacentHTML(
      "beforeend",
      '<div class="loading-inline" id="loading-bar" role="progressbar" aria-label="Loading finances"></div>',
    );
  }
  try {
    const result = await api(`state?month=${encodeURIComponent(state.month)}`);
    if (requestId !== state.requestId) return;
    state.data = result;
    state.session.user = result.user || state.session.user;
    render();
  } finally {
    state.loading = false;
    document.querySelectorAll("#loading-bar").forEach((e) => e.remove());
  }
}
function currentRoute() {
  const path = location.pathname.replace(/^\/+|\/+$/g, "");
  return routes.includes(path) ? path : "dashboard";
}
function navigate(route) {
  if (!routes.includes(route)) return;
  state.route = route;
  const path = route === "dashboard" ? "/" : `/${route}/`;
  if (location.pathname !== path) history.pushState({}, "", path);
  render();
  window.scrollTo({ top: 0, behavior: "instant" });
  document.querySelector("#page-title")?.focus({ preventScroll: true });
}
function empty(
  title,
  description,
  action,
  label,
  ico = "wallet",
  compact = false,
) {
  return `<div class="empty-state ${compact ? "compact" : ""}"><div class="empty-visual">${icon(ico)}</div><h3>${esc(title)}</h3><p>${esc(description)}</p>${action ? button(label, action, "plus", "btn-secondary") : ""}</div>`;
}
function renderAuth() {
  document.title = `${state.authMode === "signup" ? "Create account" : "Welcome back"} · FinanceFlow`;
  const signup = state.authMode === "signup";
  app.innerHTML = `<main id="main-content" class="auth-shell"><section class="auth-story" aria-label="About FinanceFlow"><a href="/" class="brand"><span class="brand-mark">f.</span><span>FinanceFlow</span></a><div class="auth-story-copy"><div class="eyebrow">A little clarity. A lot of possibility.</div><h1>Your money.<br>Your rhythm.<br><span>Your next chapter.</span></h1><p>A calmer place to manage your everyday money and make room for the things that matter.</p><div class="auth-benefits"><div>${icon("shield")}Private by design</div><div>${icon("target")}Built around your goals</div></div><div class="auth-mini-card" aria-hidden="true"><div class="auth-mini-top">Small steps, lasting progress<span>Your own pace</span></div><strong>Make space for your future.</strong><div class="auth-mini-bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><p>A little intention goes a long way.</p></div></div><div class="auth-story-footer">${icon("leaf")}A fresh perspective on your finances.</div><div class="auth-orbit" aria-hidden="true"></div></section><section class="auth-form-side"><div class="auth-top"><select class="language-select" data-language aria-label="Language"><option value="en" ${state.locale === "en" ? "selected" : ""}>EN</option><option value="pl" ${state.locale === "pl" ? "selected" : ""}>PL</option></select>${signup ? "Already have an account?" : "New to FinanceFlow?"}${button(signup ? "Sign in" : "Create an account", "auth-switch", "", "btn-secondary")}</div><div class="auth-form-wrap"><div class="eyebrow">Your money, in focus</div><h2>${signup ? "Start your next chapter." : "Welcome back."}</h2><p class="subtitle">${signup ? "Create your account and give your money a little more direction." : "A little check-in can make a big difference.<br>Sign in to see where you stand."}</p><form class="auth-form" data-form="auth"><div class="form-error" role="alert"></div>${signup ? '<div class="form-field"><label for="auth-name">First name</label><input id="auth-name" name="first_name" autocomplete="given-name" maxlength="150" placeholder="Your first name" required></div>' : ""}<div class="form-field"><label for="auth-email">Email address</label><input id="auth-email" name="email" type="email" autocomplete="email" maxlength="150" placeholder="you@example.com" required></div><div class="form-field"><label for="auth-password">Password</label><input id="auth-password" name="password" type="password" autocomplete="${signup ? "new-password" : "current-password"}" ${signup ? 'minlength="10"' : ""} maxlength="128" placeholder="${signup ? "Create a strong password" : "Enter your password"}" required>${signup ? '<p class="field-help">Use at least 10 characters. Avoid common passwords or personal details.</p>' : ""}</div>${signup ? '<div class="form-field"><label for="auth-confirm">Confirm password</label><input id="auth-confirm" name="password_confirm" type="password" autocomplete="new-password" minlength="10" maxlength="128" placeholder="Enter your password again" required></div>' : ""}<button class="btn btn-primary" type="submit">${signup ? "Create account" : "Sign in"}${icon("arrow", "small")}</button></form><p class="auth-footnote">${icon("lock")}Your finances stay in your account.</p></div><div class="auth-bottom">FinanceFlow · Less guesswork. More peace of mind.</div></section></main>`;
  translateDOM(app);
}
function render() {
  if (!state.session?.authenticated) return renderAuth();
  if (!state.data) return;
  const page = state.route;
  document.title = `${labels[page]} · FinanceFlow`;
  app.innerHTML = `<aside class="sidebar" id="sidebar" aria-label="Main navigation"><a href="/" data-route="dashboard" class="brand"><span class="brand-mark">f.</span><span class="brand-word">FinanceFlow</span></a><button class="icon-btn mobile-close" aria-label="Close navigation" data-action="close-nav">${icon("close")}</button><div class="nav-section-label">YOUR WORKSPACE</div><nav class="nav-list">${["dashboard", "transactions", "wallets", "goals", "planner", "reports", "recurring"].map((r) => `<a href="/${r === "dashboard" ? "" : r + "/"}" data-route="${r}" class="nav-link ${page === r ? "active" : ""}" ${page === r ? 'aria-current="page"' : ""} title="${labels[r]}">${icon(routeIcons[r])}<span>${labels[r]}</span></a>`).join("")}</nav><div class="nav-section-label secondary">MORE</div><nav class="nav-list secondary-nav">${["coach", "settings"].map((r) => `<a href="/${r}/" data-route="${r}" class="nav-link ${page === r ? "active" : ""}" ${page === r ? 'aria-current="page"' : ""} title="${labels[r]}">${icon(routeIcons[r])}<span>${labels[r]}</span></a>`).join("")}</nav><div class="sidebar-bottom"><div class="sidebar-note"><div class="note-icon">${icon("leaf", "small")}</div><h4>A little progress, every day.</h4><p>Small money habits.<br>A more confident you.</p></div><div class="sidebar-profile"><div class="avatar">${esc(initials())}</div><div class="profile-copy"><strong>${esc(state.session.user.first_name || "Your account")}</strong><span>Personal workspace</span></div><button class="icon-btn" data-action="logout" aria-label="Sign out" title="Sign out">${icon("logout", "small")}</button></div></div></aside><button class="sidebar-overlay" data-action="close-nav" aria-label="Close navigation" tabindex="-1"></button><div class="app-shell"><header class="topbar"><div class="topbar-left"><button class="icon-btn mobile-menu" aria-label="Open navigation" aria-controls="sidebar" aria-expanded="false" data-action="open-nav">${icon("menu")}</button><div class="breadcrumb">${icon("home")}<span class="crumb-root">Workspace</span><span class="crumb-separator">/</span><strong>${labels[page]}</strong></div></div><div class="topbar-tools"><select class="language-select" data-language aria-label="Language"><option value="en" ${state.locale === "en" ? "selected" : ""}>EN</option><option value="pl" ${state.locale === "pl" ? "selected" : ""}>PL</option></select><span class="topbar-date">${icon("calendar", "small")}${esc(new Date().toLocaleDateString(localeTag(), { day: "numeric", month: "long", year: "numeric" }))}</span><span class="topbar-divider"></span><a href="/settings/" data-route="settings" class="avatar topbar-avatar" aria-label="Account settings">${esc(initials())}</a></div></header><main class="main-content" id="main-content">${renderPage()}<footer class="footer-note">${icon("lock")}Your space. Your numbers. Your next move.</footer></main></div>`;
  translateDOM(app);
}
function monthPicker() {
  return `<label class="month-select">${icon("calendar")}<span class="sr-only">Reporting month</span><input type="month" name="month" data-action="month" value="${esc(state.month)}" min="1900-01" max="9998-12" required></label>`;
}
function pageHeading(title, description, actions = "") {
  return `<div class="page-heading"><div><h1 id="page-title" tabindex="-1">${esc(title)}</h1><p>${esc(description)}</p></div>${actions ? `<div class="page-actions">${actions}</div>` : ""}</div>`;
}
function statCard(title, value, unit, meta, ico, primary = false) {
  return `<section class="card stat-card ${primary ? "primary" : ""}"><div class="stat-top"><span>${esc(title)}</span><span class="stat-icon">${icon(ico)}</span></div><div class="stat-value">${esc(value)}${unit ? `<span class="stat-unit">${esc(unit)}</span>` : ""}</div><div class="stat-meta">${icon(primary ? "wallet" : "info")}<span>${esc(meta)}</span></div>${primary ? '<div class="stat-flourish" aria-hidden="true"></div>' : ""}</section>`;
}
function renderPage() {
  return {
    dashboard: dashboardPage,
    transactions: transactionsPage,
    wallets: walletsPage,
    goals: goalsPage,
    planner: plannerPage,
    reports: reportsPage,
    recurring: recurringPage,
    settings: settingsPage,
    coach: coachPage,
  }[state.route]();
}
function dashboardPage() {
  const d = state.data,
    s = d.summary,
    currency = d.profile.currency;
  const tx = d.transactions.slice(0, 5);
  return `${pageHeading(`Let's make it a good month, ${firstName()}.`, "A clear view of your money. A little more room to breathe.", `${monthPicker()}${button("Add transaction", "add-transaction")}`)}<div class="stat-grid">${statCard("Total balance", plainMoney(s.balance), currency, "Active wallets · through today", "wallet", true)}${statCard("Money in", plainMoney(s.income), currency, `Income · ${monthLabel(state.month)}`, "down")}${statCard("Money out", plainMoney(s.expenses), currency, `Expenses · ${monthLabel(state.month)}`, "up")}${statCard("Savings rate", `${num(s.savings_rate).toFixed(1)}%`, "", num(s.income) > 0 ? "Share of income left after expenses" : "Add income to see your savings rate", "leaf")}</div><div class="dashboard-middle"><section class="card card-padding"><div class="card-header"><div><h2>Cash flow</h2><p>The bigger picture, one month at a time.</p></div><div class="chart-legend"><span class="legend-item"><i class="legend-dot"></i>Income</span><span class="legend-item"><i class="legend-dot lime"></i>Expenses</span></div></div>${cashFlowChart(d.trend)}${!d.trend.some((x) => num(x.income) || num(x.expense)) ? '<p class="chart-empty-note">Your monthly story starts with your first transaction.</p>' : ""}</section><section class="card card-padding"><div class="card-header"><div><h2>Where your money goes</h2><p>Your spending, at a glance.</p></div>${routeLink("Details", "reports")}</div>${spendingDonut()}<div class="spending-legend">${spendingLegend()}</div><div class="spending-note">${icon("leaf")}${num(s.expenses) > 0 ? "Category percentages are rounded." : "Add an expense to see your spending breakdown."}</div></section></div><div class="dashboard-bottom"><section class="card card-padding"><div class="card-header"><div><h2>Recent transactions</h2><p>The little things that add up.</p></div>${routeLink("View all", "transactions")}</div>${tx.length ? transactionsTable(tx, true) : empty("A fresh start for your finances", "Add an income or expense. Your latest activity will appear here.", "add-transaction", "Add your first transaction", "arrows", true)}</section><section class="card card-padding"><div class="card-header"><div><h2>Making room for more</h2><p>Your savings goals, a little closer.</p></div>${routeLink("View all", "goals")}</div>${
    d.goals.length
      ? d.goals
          .slice(0, 3)
          .map((goal) => goalMini(goal))
          .join("")
      : empty(
          "Something worth saving for",
          "A trip, a rainy day, a new beginning. Give your next goal a name.",
          "add-goal",
          "Create a goal",
          "target",
          true,
        )
  }</section></div>${!d.wallets.length ? `<div class="gentle-banner">${icon("wallet")}<div><strong>A good place to begin: your first wallet.</strong><p>Add an account or cash wallet, then start tracking your money.</p></div>${button("Add wallet", "add-wallet", "plus", "btn-secondary btn-small")}</div>` : `<div class="gentle-banner">${icon("leaf")}<div><strong>A little plan goes a long way.</strong><p>Give every part of your income a purpose with a budget that fits you.</p></div><a href="/planner/" data-route="planner" class="btn btn-secondary btn-small">Your budget ${icon("arrow", "small")}</a></div>`}`;
}
function cashFlowChart(trend) {
  const items = (trend || []).slice(-6);
  const data = items.length
    ? items
    : Array.from({ length: 6 }, (_, i) => {
        const date = new Date(`${state.month}-02T12:00:00`);
        date.setMonth(date.getMonth() - 5 + i);
        return {
          label: date.toLocaleDateString(localeTag(), { month: "short" }),
          income: 0,
          expense: 0,
        };
      });
  const max = Math.max(
    100,
    ...data.flatMap((x) => [num(x.income), num(x.expense)]),
  );
  const power = 10 ** Math.floor(Math.log10(max));
  const ceiling = Math.ceil(max / power) * power;
  const left = 44,
    top = 14,
    height = 150,
    width = 460,
    step = width / data.length;
  return `<figure class="chart-figure" aria-label="Income and expenses over the last six months"><svg class="chart" viewBox="0 0 525 201" role="img"><title>Monthly income and expenses</title><desc>${esc(data.map((x) => `${x.label || x.month}: income ${money(x.income)}, expenses ${money(x.expense)}`).join(". "))}</desc>${Array.from(
    { length: 4 },
    (_, i) => {
      const y = top + (height * i) / 3;
      return `<line x1="${left}" y1="${y}" x2="510" y2="${y}"/><text x="0" y="${y + 4}">${esc(compactMoney((ceiling * (3 - i)) / 3))}</text>`;
    },
  ).join("")}${data
    .map((x, i) => {
      const center = left + step * (i + 0.5),
        iw = (num(x.income) / ceiling) * height,
        ew = (num(x.expense) / ceiling) * height;
      return `<g><title>${esc(x.label || x.month)}: income ${esc(money(x.income))}, expenses ${esc(money(x.expense))}</title><rect class="income" x="${center - 20}" y="${top + height - iw}" width="16" height="${iw}" rx="3"/><rect class="expense" x="${center + 3}" y="${top + height - ew}" width="16" height="${ew}" rx="3"/><text x="${center}" y="192" text-anchor="middle">${esc(x.label || new Date(`${x.month}-02T12:00:00`).toLocaleDateString(localeTag(), { month: "short" }))}</text></g>`;
    })
    .join("")}</svg></figure>`;
}
function donutSVG(segments) {
  const radius = 72,
    circumference = 2 * Math.PI * radius,
    total = segments.reduce((sum, x) => sum + Math.max(0, num(x.value)), 0);
  let consumed = 0;
  return `<svg class="donut-svg" viewBox="0 0 200 200" aria-hidden="true"><circle class="donut-track" cx="100" cy="100" r="${radius}"/>${
    total > 0
      ? segments
          .map((s, i) => {
            const ratio = Math.max(0, num(s.value)) / total,
              full = ratio * circumference,
              gap =
                segments.filter((x) => num(x.value) > 0).length > 1
                  ? Math.min(3, full * 0.15)
                  : 0;
            const result = `<circle class="donut-segment" cx="100" cy="100" r="${radius}" stroke="${colors[i % colors.length]}" stroke-dasharray="${Math.max(0, full - gap)} ${circumference - Math.max(0, full - gap)}" stroke-dashoffset="${-consumed}"/>`;
            consumed += full;
            return result;
          })
          .join("")
      : ""
  }</svg>`;
}
function spendingGroups() {
  const all = state.data.category_spending || [];
  if (all.length <= 5) return all;
  return [
    ...all.slice(0, 4),
    {
      name: "Other",
      amount: all.slice(4).reduce((s, x) => s + num(x.amount), 0),
      percent: all.slice(4).reduce((s, x) => s + num(x.percent), 0),
    },
  ];
}
function spendingDonut() {
  const groups = spendingGroups();
  return `<div class="spending-visual">${donutSVG(groups.map((x) => ({ value: x.amount })))}<div class="donut-center"><span>Total spent</span><strong>${esc(money(state.data.summary.expenses))}</strong><small>${esc(monthLabel(state.month))}</small></div></div>`;
}
function spendingLegend() {
  const groups = spendingGroups(),
    classes = ["", "lime", "purple", "orange", "sage"];
  return groups.length
    ? groups
        .map(
          (x, i) =>
            `<div class="legend-item"><i class="legend-dot ${classes[i % classes.length]}"></i><span>${esc(x.name)}</span><strong>${num(x.percent).toFixed(1)}%</strong></div>`,
        )
        .join("")
    : '<div class="legend-item"><i class="legend-dot gray"></i><span>No spending yet</span><strong>0%</strong></div>';
}
function goalMini(g) {
  return `<div class="goal-mini"><div class="goal-mini-top"><span class="goal-mini-name"><span class="goal-mini-icon">${icon("target")}</span>${esc(g.name)}</span><span>${num(g.progress).toFixed(0)}%</span></div><progress value="${num(g.progress)}" max="100" aria-label="${esc(g.name)} progress"></progress><div class="goal-mini-amounts"><strong>${esc(money(g.saved_amount))}</strong><span>of ${esc(money(g.target_amount))}</span></div></div>`;
}
function transactionsTable(transactions, compact = false) {
  return `<div class="table-wrap"><table class="${compact ? "" : "transactions-table"}"><thead><tr><th>Transaction</th>${compact ? "<th>Category</th><th>Date</th>" : "<th>Amount</th><th>Category</th><th>Wallet</th><th>Date</th>"}${compact ? '<th class="text-right">Amount</th>' : '<th class="text-right">Actions</th>'}</tr></thead><tbody>${transactions.map((t) => `<tr><td><div class="transaction-cell"><span class="category-icon">${icon(categoryIcon(t.category))}</span><span><strong class="transaction-title" title="${esc(t.title)}">${esc(t.title)}</strong><span class="transaction-subtitle">${esc(compact ? walletName(t.wallet) : t.kind === "income" ? "Income" : "Expense")}</span></span></div></td>${compact ? `<td><span class="pill ${t.kind === "income" ? "green" : ""}">${esc(categoryName(t.category))}</span></td><td>${esc(shortDate(t.date))}</td><td class="text-right amount ${t.kind}">${t.kind === "income" ? "+" : "−"}${esc(money(t.amount))}</td>` : `<td class="amount ${t.kind}">${t.kind === "income" ? "+" : "−"}${esc(money(t.amount))}</td><td><span class="pill ${t.kind === "income" ? "green" : ""}">${esc(categoryName(t.category))}</span></td><td>${esc(walletName(t.wallet))}</td><td>${esc(shortDate(t.date))}</td><td><div class="table-actions"><button class="icon-btn" data-action="edit-transaction" data-id="${num(t.id)}" aria-label="Edit ${esc(t.title)}">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-transaction" data-id="${num(t.id)}" aria-label="Delete ${esc(t.title)}">${icon("trash")}</button></div></td>`}</tr>`).join("")}</tbody></table></div>`;
}
function filteredTransactions() {
  const f = state.filters;
  return state.data.transactions.filter(
    (t) =>
      (f.kind === "all" || t.kind === f.kind) &&
      (f.wallet === "all" || String(t.wallet) === f.wallet) &&
      `${t.title} ${t.note} ${categoryName(t.category)} ${walletName(t.wallet)}`
        .toLowerCase()
        .includes(f.search.toLowerCase()),
  );
}
function transactionsPage() {
  const list = filteredTransactions();
  return `${pageHeading("Every little transaction.", "See what comes in, what goes out, and what it means.", `${monthPicker()}${button("Add transaction", "add-transaction")}`)}<section class="card card-padding"><div class="list-toolbar"><label class="search-field"><span class="sr-only">Search transactions</span>${icon("search")}<input type="search" id="transaction-search" placeholder="Search transactions…" value="${esc(state.filters.search)}"></label><label><span class="sr-only">Transaction type</span><select data-filter="kind"><option value="all">All transactions</option><option value="income" ${state.filters.kind === "income" ? "selected" : ""}>Income</option><option value="expense" ${state.filters.kind === "expense" ? "selected" : ""}>Expenses</option></select></label><label><span class="sr-only">Wallet</span><select data-filter="wallet"><option value="all">All wallets</option>${state.data.wallets.map((w) => `<option value="${num(w.id)}" ${state.filters.wallet === String(w.id) ? "selected" : ""}>${esc(w.name)}</option>`).join("")}</select></label>${button("Export", "export", "download", "btn-secondary")}</div><div id="transaction-results">${transactionResults(list)}</div></section>`;
}
function transactionResults(list) {
  return list.length
    ? `${transactionsTable(list)}<div class="filters-info">${list.length} transaction${list.length === 1 ? "" : "s"} · ${esc(monthLabel(state.month))}</div>`
    : empty(
        state.data.transactions.length
          ? "No transactions match your filters"
          : "Your money story starts here",
        state.data.transactions.length
          ? "Try a different search or another wallet."
          : "Add your income and expenses to start seeing the bigger picture.",
        state.data.transactions.length ? "reset-filters" : "add-transaction",
        state.data.transactions.length ? "Clear filters" : "Add a transaction",
        "arrows",
      );
}
function walletsPage() {
  const d = state.data;
  return `${pageHeading("A home for your money.", "Keep your accounts and cash in one clear view.", button("Add wallet", "add-wallet"))}<div class="toolbar-summary"><p>Current balance across active wallets <strong>${esc(money(d.summary.balance))}</strong></p><span class="pill green">${d.wallets.filter((w) => w.is_active).length} active wallet${d.wallets.filter((w) => w.is_active).length === 1 ? "" : "s"}</span></div>${d.wallets.length ? `<div class="entity-grid">${d.wallets.map((w, i) => `<section class="card entity-card wallet-card ${i === 0 ? "featured" : ""}"><div class="row between"><span class="category-icon">${icon(w.wallet_type === "card" ? "card" : w.wallet_type === "cash" ? "cash" : "wallet")}</span><div class="table-actions"><button class="icon-btn" data-action="edit-wallet" data-id="${num(w.id)}" aria-label="Edit ${esc(w.name)}">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-wallet" data-id="${num(w.id)}" aria-label="Delete ${esc(w.name)}">${icon("trash")}</button></div></div><h3>${esc(w.name)}</h3><div class="entity-label">${esc(w.wallet_type)} wallet ${w.is_active ? "" : "· archived"}</div><div class="entity-value">${esc(money(w.balance))}</div><div class="entity-foot"><span>Opening balance ${esc(money(w.opening_balance))}</span>${icon("wallet", "small")}</div></section>`).join("")}<button class="add-card" data-action="add-wallet">${icon("plus")}Add another wallet</button></div>` : `<section class="card">${empty("Bring your money together", "Add a bank account, a savings account, or a cash wallet. You enter and manage the balances yourself.", "add-wallet", "Add your first wallet", "wallet")}</section>`}<p class="info-box">Current balances include your opening balance and transactions through today. Future transactions are included when their date arrives. Wallets are tracked manually; they are not connected to a bank.</p>`;
}
function goalsPage() {
  const goals = state.data.goals;
  return `${pageHeading("Good things worth saving for.", "Make your next chapter a little more tangible.", button("Create goal", "add-goal"))}${goals.length ? `<div class="entity-grid">${goals.map((g) => `<section class="card entity-card goal-card"><div class="row between"><span class="category-icon">${icon("target")}</span><div class="table-actions"><button class="icon-btn" data-action="edit-goal" data-id="${num(g.id)}" aria-label="Edit ${esc(g.name)}">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-goal" data-id="${num(g.id)}" aria-label="Delete ${esc(g.name)}">${icon("trash")}</button></div></div><h3>${esc(g.name)}</h3><div class="entity-value">${esc(money(g.saved_amount))} <span>of ${esc(money(g.target_amount))}</span></div><progress value="${num(g.progress)}" max="100" aria-label="${esc(g.name)} progress"></progress><div class="progress-label"><span>${num(g.progress).toFixed(1)}% of the way there</span><span>${num(g.remaining) > 0 ? esc(money(g.remaining)) + " to go" : "Goal reached"}</span></div><div class="entity-foot"><span>${icon("calendar", "small")}</span><span>${esc(g.target_date ? `Target: ${dateLabel(g.target_date)}` : "Your goal, your own pace")}</span>${button("Update", "edit-goal", "edit", "btn-secondary btn-small", `data-id="${num(g.id)}"`)}</div></section>`).join("")}<button class="add-card" data-action="add-goal">${icon("plus")}Make room for a new goal</button></div>` : `<section class="card">${empty("What are you looking forward to?", "A little emergency fund or a big adventure. Set a target and update your progress whenever you save.", "add-goal", "Create your first goal", "target")}</section>`}<p class="info-box">Goals are your personal savings tracker. Updating a saved amount does not transfer money or change a wallet balance.</p>`;
}
function plannerPage() {
  const p = state.data.plan;
  return `${pageHeading("A plan that feels like you.", "Give your income a purpose. Make room for life.", monthPicker())}<div class="planner-grid"><section class="card card-padding"><div class="card-header"><div><h2>Your income allocation</h2><p>You choose the percentages. We work out the rest.</p></div><span class="pill green">Your plan</span></div><p class="planner-intro">Split your planning income between essentials, everyday joys, and your future. Adjust any number below; the preview updates as you type.</p><form data-form="plan" id="plan-form"><div class="form-error" role="alert"></div>${[
    {
      key: "essential_pct",
      label: "Essentials",
      help: "Home, groceries, bills, and everyday needs.",
      ico: "home",
    },
    {
      key: "lifestyle_pct",
      label: "Lifestyle",
      help: "The little things that make life yours.",
      ico: "coffee",
    },
    {
      key: "savings_pct",
      label: "Savings",
      help: "Your goals and a little peace of mind.",
      ico: "leaf",
    },
  ]
    .map(
      (x) =>
        `<div class="plan-field"><span class="category-icon">${icon(x.ico)}</span><div class="plan-label"><label for="${x.key}"><strong>${x.label}</strong></label><p>${x.help}</p></div><div class="input-unit"><input id="${x.key}" name="${x.key}" type="text" inputmode="decimal" data-decimal min="0" max="100" value="${esc(p[x.key])}" required><span>%</span></div></div>`,
    )
    .join(
      "",
    )}<div class="plan-total" id="plan-total"><span>Total allocation</span><strong>100%</strong></div><p class="field-help" id="plan-help">Your percentages must add up to 100%. Changes are applied when you save.</p><div class="form-actions">${button("Reset", "reset-plan", "", "btn-secondary")}<button class="btn btn-primary" type="submit">${icon("check", "small")}Save allocation</button></div></form></section><section class="card card-padding plan-preview"><div class="card-header"><div><h2>Your monthly plan</h2><p>Preview based on ${esc(money(p.planning_income))} of income.</p></div><span class="pill" id="plan-preview-state">Saved</span></div><div id="plan-donut" class="spending-visual">${planDonut([p.essential_pct, p.lifestyle_pct, p.savings_pct])}</div><div id="plan-amounts" class="plan-amounts">${planAmounts([p.essential_pct, p.lifestyle_pct, p.savings_pct])}</div><div class="info-box">Planning income uses the greater of your expected income and income recorded for ${esc(monthLabel(state.month))}. ${routeLink("Set expected income", "settings")}</div></section></div><section class="card card-padding budget-list"><div class="card-header"><div><h2>Keep everyday spending in balance</h2><p>Set a monthly limit for the categories you want to watch.</p></div>${button("Add limit", "add-budget", "plus", "btn-secondary btn-small")}</div>${state.data.budgets.length ? state.data.budgets.map((b) => `<div class="budget-row ${num(b.percent) > 100 ? "over" : ""}"><span class="category-icon">${icon(categoryIcon(b.category))}</span><div class="budget-copy"><strong>${esc(categoryName(b.category))}</strong><p>${esc(money(b.spent))} spent of ${esc(money(b.monthly_limit))}</p><progress max="100" value="${Math.min(100, num(b.percent))}" aria-label="${esc(categoryName(b.category))} budget used"></progress></div><div class="budget-amounts"><strong>${num(b.percent).toFixed(0)}% used</strong><small>${num(b.remaining) < 0 ? esc(money(Math.abs(num(b.remaining)))) + " over" : esc(money(b.remaining)) + " left"}</small></div><div class="table-actions"><button class="icon-btn" data-action="edit-budget" data-id="${num(b.id)}" aria-label="Edit ${esc(categoryName(b.category))} limit">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-budget" data-id="${num(b.id)}" aria-label="Delete ${esc(categoryName(b.category))} limit">${icon("trash")}</button></div></div>`).join("") : empty("A little boundary can go a long way", "Add a spending limit for groceries, dining out, or another category.", "add-budget", "Set a category limit", "pie", true)}</section><p class="info-box">Your allocation is a planning target. Actual spending charts and savings rate are calculated from your transactions and do not change when you edit these percentages.</p>`;
}
// Match the server's largest-remainder cent allocation, including one-cent budgets.
function allocateCents(income, shares) {
  const cents = BigInt(Math.round(num(income) * 100));
  const values = shares.map((s) =>
    BigInt(Math.round(Math.max(0, num(s)) * 100)),
  );
  const total = values.reduce((a, b) => a + b, 0n);
  if (total <= 0n) return [0, 0, 0];
  const numerators = values.map((v) => cents * v);
  const result = numerators.map((v) => v / total);
  const remainder = Number(cents - result.reduce((a, b) => a + b, 0n));
  const order = numerators
    .map((v, i) => ({ i, remainder: v % total }))
    .sort((a, b) =>
      a.remainder === b.remainder
        ? a.i - b.i
        : a.remainder > b.remainder
          ? -1
          : 1,
    );
  for (let i = 0; i < remainder; i++) result[order[i % order.length].i] += 1n;
  return result.map((v) => Number(v) / 100);
}
function planDonut(shares) {
  return `${donutSVG(shares.map((value) => ({ value })))}<div class="donut-center"><span>Planning income</span><strong>${esc(money(state.data.plan.planning_income))}</strong><small>Make every part count.</small></div>`;
}
function planAmounts(shares) {
  const amounts = allocateCents(state.data.plan.planning_income, shares);
  return ["Essentials", "Lifestyle", "Savings"]
    .map(
      (label, i) =>
        `<div class="plan-amount-row"><span><i class="legend-dot ${["", "lime", "purple"][i]}"></i>${label}</span><strong>${esc(money(amounts[i]))}</strong></div>`,
    )
    .join("");
}
function updatePlanPreview() {
  const form = document.querySelector("#plan-form");
  if (!form) return;
  const keys = ["essential_pct", "lifestyle_pct", "savings_pct"];
  const shares = keys.map((key) => num(form.elements[key].value));
  const cents = shares.reduce((s, x) => s + Math.round(x * 100), 0);
  const valid =
    cents === 10000 &&
    shares.every((x) => x >= 0 && x <= 100) &&
    keys.every((k) => form.elements[k].validity.valid);
  const total = document.querySelector("#plan-total");
  total.classList.toggle("invalid", !valid);
  total.innerHTML = `<span>Total allocation</span><strong>${(cents / 100).toFixed(cents % 100 ? 2 : 0)}%</strong>`;
  document.querySelector("#plan-help").textContent = valid
    ? "Ready to save. Your percentages add up to 100%."
    : `Your percentages must total 100%. ${cents < 10000 ? `Add ${((10000 - cents) / 100).toFixed(2)}%.` : `Reduce by ${((cents - 10000) / 100).toFixed(2)}%.`}`;
  form.querySelector("[type=submit]").disabled = !valid;
  document.querySelector("#plan-donut").innerHTML = planDonut(shares);
  document.querySelector("#plan-amounts").innerHTML = valid
    ? planAmounts(shares)
    : '<p class="field-help">Set your percentages to a total of 100% to calculate the amounts.</p>';
  const changed = keys.some(
    (k, i) =>
      Math.round(shares[i] * 100) !== Math.round(num(state.data.plan[k]) * 100),
  );
  document.querySelector("#plan-preview-state").textContent = changed
    ? "Unsaved preview"
    : "Saved";
}
function reportsPage() {
  const d = state.data,
    s = d.summary;
  return `${pageHeading("A little perspective changes things.", "See the patterns behind your everyday money.", `${monthPicker()}${button("Export report", "export", "download", "btn-secondary")}`)}<div class="stats-three">${statCard("Income this month", plainMoney(s.income), d.profile.currency, "All recorded income in the selected month", "down", true)}${statCard("Expenses this month", plainMoney(s.expenses), d.profile.currency, "All recorded expenses in the selected month", "up")}${statCard("Money left", plainMoney(s.net), d.profile.currency, "Income minus expenses in the selected month", "leaf")}</div><div class="report-grid"><section class="card card-padding"><div class="card-header"><div><h2>Your money over time</h2><p>Six months of income and expenses.</p></div><div class="chart-legend"><span class="legend-item"><i class="legend-dot"></i>Income</span><span class="legend-item"><i class="legend-dot lime"></i>Expenses</span></div></div>${cashFlowChart(d.trend)}<div class="info-box">${num(s.income) > 0 ? `You have ${num(s.net) >= 0 ? "kept" : "spent beyond your income"} ${esc(money(Math.abs(num(s.net))))} this month. Your savings rate is ${num(s.savings_rate).toFixed(1)}%.` : "Record your income and expenses to start understanding your money habits."}</div></section><section class="card card-padding"><div class="card-header"><div><h2>Your spending mix</h2><p>${esc(monthLabel(state.month))}</p></div></div>${spendingDonut()}<div class="spending-legend">${spendingLegend()}</div></section></div><section class="card card-padding budget-list"><div class="card-header"><div><h2>One category at a time</h2><p>The details behind your total expenses.</p></div></div>${d.category_spending.length ? d.category_spending.map((c) => `<div class="report-category"><span class="category-icon">${icon(categoryIcon(c.category))}</span><div class="category-name">${esc(c.name)}<progress value="${num(c.percent)}" max="100" aria-label="${esc(c.name)} share of expenses"></progress></div><div class="category-total">${esc(money(c.amount))}<small>${num(c.percent).toFixed(1)}% of spending</small></div></div>`).join("") : empty("Your spending picture is still a blank canvas", "Add an expense and its category to see it here.", "add-transaction", "Add an expense", "chart", true)}</section>`;
}
function recurringPage() {
  const items = state.data.recurring;
  return `${pageHeading("One less thing to remember.", "Keep your regular bills and income in a steady rhythm.", button("Add recurring payment", "add-recurring"))}<div class="toolbar-summary"><p>Record payments due in <strong>${esc(monthLabel(state.month))}</strong>.<br>Each payment is recorded once per month.</p><div class="row wrap">${monthPicker()}${button("Apply due payments", "apply-recurring", "repeat", "btn-secondary", state.month > today().slice(0, 7) ? 'disabled title="Future payments are not due yet"' : "")}</div></div>${items.length ? `<div class="entity-grid">${items.map((r) => `<section class="card entity-card recurring-card ${r.is_active ? "" : "paused"}"><div class="row between"><span class="category-icon">${icon(categoryIcon(r.category))}</span><div class="table-actions"><button class="icon-btn" data-action="edit-recurring" data-id="${num(r.id)}" aria-label="Edit ${esc(r.title)}">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-recurring" data-id="${num(r.id)}" aria-label="Delete ${esc(r.title)}">${icon("trash")}</button></div></div><h3>${esc(r.title)}</h3><div class="recurring-frequency">${icon("calendar")}Monthly · day ${num(r.day_of_month)}</div><div class="entity-value">${r.kind === "income" ? "+" : "−"}${esc(money(r.amount))}</div><div class="entity-foot"><span>${esc(walletName(r.wallet))}</span><span class="pill ${r.is_active ? "green" : ""}">${r.is_active ? "Active" : "Paused"}</span></div></section>`).join("")}</div>` : `<section class="card">${empty("A routine that works for you", "Add rent, subscriptions, salary, or another regular payment. Apply due payments when you are ready.", "add-recurring", "Add a recurring payment", "repeat")}</section>`}<p class="info-box">Payments are recorded only when you select “Apply due payments”. Days 29–31 move to the last day in shorter months. Only payments due on or before today are applied; repeating the action does not add duplicates.</p>`;
}
function settingsPage() {
  const d = state.data;
  return `${pageHeading("Your space, your preferences.", "A few small details to make FinanceFlow feel like yours.")}<div class="settings-layout"><div><section class="card card-padding settings-section"><h3>The essentials</h3><p class="section-subtitle">Keep your profile and planning details up to date.</p><div class="settings-account"><div class="avatar">${esc(initials())}</div><div><strong>${esc(d.user.first_name || "Your account")}</strong><p>${esc(d.user.email)}</p></div></div><form data-form="settings"><div class="form-error" role="alert"></div><div class="form-grid"><div class="form-field"><label for="first-name">First name</label><input id="first-name" name="first_name" value="${esc(d.user.first_name)}" maxlength="150" autocomplete="given-name" required></div><div class="form-field"><label for="currency">Display currency</label><select id="currency" name="currency">${["PLN", "EUR", "USD", "GBP", "KGS"].map((c) => `<option value="${c}" ${d.profile.currency === c ? "selected" : ""}>${c}</option>`).join("")}</select></div><div class="form-field full"><label for="expected-income">Expected monthly income</label><div class="input-unit"><input id="expected-income" name="expected_monthly_income" type="text" inputmode="decimal" data-decimal min="0" max="9999999999.99" value="${esc(d.profile.expected_monthly_income)}" required><span>${esc(d.profile.currency)}</span></div><p class="field-help">Your budget uses this amount when it is higher than your recorded monthly income.</p></div></div><p class="currency-note">Changing your display currency changes labels only. Existing amounts are not converted between currencies.</p><div class="form-actions"><button class="btn btn-primary" type="submit">${icon("check", "small")}Save preferences</button></div></form></section><section class="card card-padding settings-section"><div class="card-header"><div><h2>Categories that fit your life</h2><p>Organize your money in a way that makes sense to you.</p></div>${button("Add", "add-category", "plus", "btn-secondary btn-small")}</div><div class="category-list">${d.categories.map((c) => `<div class="category-row"><span class="category-icon">${icon(categoryIcon(c.id))}</span><span class="category-label">${esc(c.name)}</span><span class="pill">${esc(c.kind === "both" ? "Income & expense" : c.kind)}</span><div class="table-actions"><button class="icon-btn" data-action="edit-category" data-id="${num(c.id)}" aria-label="Edit ${esc(c.name)}">${icon("edit")}</button><button class="icon-btn danger" data-action="delete-category" data-id="${num(c.id)}" aria-label="Delete ${esc(c.name)}">${icon("trash")}</button></div></div>`).join("")}</div></section></div><div><section class="card card-padding settings-section"><h3>A little peace of mind</h3><p class="section-subtitle">Your account keeps your money records in your own workspace.</p><div class="security-item">${icon("lock")}<div><strong>Private account access</strong><p>Your financial records are available only after signing in to your account.</p></div></div><div class="security-item">${icon("shield")}<div><strong>Protected sessions</strong><p>Account sessions and form requests use built-in security checks.</p></div></div><div class="security-item">${icon("download")}<div><strong>Your data, within reach</strong><p>Download your monthly transaction records whenever you need them.</p></div></div><div class="form-actions">${button("Export " + monthLabel(state.month), "export", "download", "btn-secondary")}</div></section><section class="card card-padding settings-section"><h3>Signing off for now?</h3><p class="section-subtitle">Your latest saved changes will be here when you return.</p>${button("Sign out", "logout", "logout", "btn-secondary")}</section></div></div>`;
}
function coachPage() {
  return `${pageHeading("Small insights. Thoughtful next steps.", "Insights for the current calendar month.")}<div class="settings-layout"><section class="card card-padding"><div class="card-header"><div><h2>Your money check-in</h2><p>A local helper with simple rules. No external AI service.</p></div><span class="category-icon">${icon("sparkles")}</span></div><div class="info-box">Ask about this month’s income, spending, savings plan or your current balance. Replies use your recorded transactions and saved budget.</div><div id="coach-messages" class="coach-messages" aria-live="polite">${coachMessages()}</div><form data-form="coach"><div class="form-error" role="alert"></div><div class="form-field"><label for="coach-message">What would you like to understand?</label><textarea id="coach-message" name="message" maxlength="1000" placeholder="For example: How can I improve my savings?" required></textarea></div><div class="form-actions"><button class="btn btn-primary" type="submit">Ask for an insight${icon("arrow", "small")}</button></div></form></section><section class="card card-padding"><h3>A useful place to start</h3><p class="planner-intro">You do not need a perfect system. Start with a few habits that are easy to repeat.</p><div class="security-item">${icon("arrows")}<div><strong>Keep your records current</strong><p>A few minutes of tracking makes your overview more useful.</p></div></div><div class="security-item">${icon("pie")}<div><strong>Give your income a purpose</strong><p>Try a budget allocation, then adjust it to fit your life.</p></div></div><div class="security-item">${icon("target")}<div><strong>Pick one meaningful goal</strong><p>A clear target makes small contributions feel more tangible.</p></div></div><p class="info-box">These are general budgeting observations based on your records, not personalized financial advice. The helper uses the current calendar month.</p></section></div>`;
}
function coachMessages() {
  return state.coachMessages
    .map(
      (m) =>
        `<div class="coach-message ${m.role === "user" ? "from-user" : ""}"><span>${m.role === "user" ? "You" : "FinanceFlow"}</span><p>${esc(m.text)}</p></div>`,
    )
    .join("");
}
const collections = {
  transaction: "transactions",
  wallet: "wallets",
  goal: "goals",
  budget: "budgets",
  recurring: "recurring",
  category: "categories",
};
const field = (
  name,
  label,
  value = "",
  type = "text",
  attrs = "",
  help = "",
  full = false,
) =>
  `<div class="form-field ${full ? "full" : ""}"><label for="field-${name}">${esc(label)}</label><input id="field-${name}" name="${name}" type="${type}" value="${esc(value)}" ${attrs}>${help ? `<p class="field-help">${esc(help)}</p>` : ""}</div>`;
const selectField = (name, label, options, value, attrs = "", full = false) =>
  `<div class="form-field ${full ? "full" : ""}"><label for="field-${name}">${esc(label)}</label><select id="field-${name}" name="${name}" ${attrs}>${options.map((o) => `<option value="${esc(o.value)}" ${String(o.value) === String(value) ? "selected" : ""} ${o.disabled ? "disabled" : ""}>${esc(o.label)}</option>`).join("")}</select></div>`;
const moneyAttrs =
  'inputmode="decimal" data-decimal min="0.01" max="9999999999.99" required';
function walletOptions(existing) {
  return state.data.wallets
    .filter((w) => w.is_active || String(w.id) === String(existing))
    .map((w) => ({
      value: w.id,
      label:
        w.name + (w.is_active ? "" : " (archived — restore or choose another)"),
    }));
}
function categoryOptions(kind, selected) {
  return [
    { value: "", label: "No category" },
    ...state.data.categories
      .filter(
        (c) =>
          c.kind === kind ||
          c.kind === "both" ||
          String(c.id) === String(selected),
      )
      .map((c) => ({ value: c.id, label: c.name })),
  ];
}
function showDialog(title, description, content) {
  state.dialogReturn = document.activeElement;
  dialog.innerHTML = `<div class="dialog-heading"><h2 id="dialog-title">${esc(title)}</h2><button type="button" class="icon-btn" data-action="close-dialog" aria-label="Close dialog">${icon("close")}</button></div><p class="dialog-description" id="dialog-description">${esc(description)}</p>${content}`;
  translateDOM(dialog);
  dialog.setAttribute("aria-describedby", "dialog-description");
  dialog.showModal();
  const first = dialog.querySelector(
    "input:not([type=hidden]),select,textarea",
  );
  if (first) first.focus();
}
function closeDialog() {
  dialog.close();
}
function openEntity(type, id) {
  const collection = collections[type],
    item = id ? findItem(collection, id) : null;
  if (id && !item) return;
  const editing = !!item,
    x = item || {},
    kind = x.kind || "expense";
  if (
    ["transaction", "recurring"].includes(type) &&
    !state.data.wallets.some((w) => w.is_active)
  ) {
    showDialog(
      "First, give your money a home.",
      "You need an active wallet before adding a transaction or recurring payment.",
      `<div class="form-actions">${button("Cancel", "close-dialog", "", "btn-secondary")}${button("Add wallet", "dialog-add-wallet")}</div>`,
    );
    return;
  }
  let content = "",
    title = "",
    description = "";
  if (type === "wallet") {
    title = editing ? "Edit wallet" : "Add a wallet";
    description = "Your account, savings, or cash — all in one place.";
    content =
      field(
        "name",
        "Wallet name",
        x.name || "",
        "text",
        'maxlength="80" required placeholder="e.g. Everyday account"',
        "",
        true,
      ) +
      selectField(
        "wallet_type",
        "Wallet type",
        [
          { value: "card", label: "Bank / card" },
          { value: "cash", label: "Cash" },
          { value: "savings", label: "Savings" },
          { value: "other", label: "Other" },
        ],
        x.wallet_type || "card",
      ) +
      field(
        "opening_balance",
        "Opening balance",
        x.opening_balance ?? "0.00",
        "text",
        'inputmode="decimal" data-decimal min="-9999999999.99" max="9999999999.99" required',
        "Balance before the transactions you record.",
      ) +
      (editing
        ? `<label class="checkbox-field full"><input name="is_active" type="checkbox" ${x.is_active ? "checked" : ""}> Active wallet</label><p class="field-help full">Archived wallets remain in your history and are excluded from your current total balance.</p>`
        : "");
  }
  if (type === "transaction") {
    title = editing ? "Edit transaction" : "Add a transaction";
    description = "A small entry. A clearer picture.";
    content =
      selectField(
        "kind",
        "Transaction type",
        [
          { value: "expense", label: "Expense" },
          { value: "income", label: "Income" },
        ],
        kind,
      ) +
      field(
        "amount",
        `Amount (${state.data.profile.currency})`,
        x.amount || "",
        "text",
        moneyAttrs,
      ) +
      field(
        "title",
        "Description",
        x.title || "",
        "text",
        'maxlength="120" required placeholder="e.g. Weekly groceries"',
        "",
        true,
      ) +
      selectField(
        "wallet",
        "Wallet",
        walletOptions(x.wallet),
        x.wallet || state.data.wallets.find((w) => w.is_active)?.id,
        "required",
      ) +
      selectField(
        "category",
        "Category",
        categoryOptions(kind, x.category),
        x.category || "",
      ) +
      field(
        "date",
        "Date",
        x.date ||
          (state.month === today().slice(0, 7) ? today() : `${state.month}-01`),
        "date",
        'min="1900-01-01" max="9998-12-31" required',
        "",
        true,
      ) +
      `<div class="form-field full"><label for="field-note">Note <span class="muted">(optional)</span></label><textarea id="field-note" name="note" maxlength="250" placeholder="Anything you would like to remember…">${esc(x.note || "")}</textarea></div>`;
  }
  if (type === "goal") {
    title = editing ? "Update your goal" : "Create a savings goal";
    description = "Name something worth making room for.";
    content =
      field(
        "name",
        "Goal name",
        x.name || "",
        "text",
        'maxlength="120" required placeholder="e.g. A little rainy-day fund"',
        "",
        true,
      ) +
      field(
        "target_amount",
        `Target (${state.data.profile.currency})`,
        x.target_amount || "",
        "text",
        moneyAttrs,
      ) +
      field(
        "saved_amount",
        `Already saved (${state.data.profile.currency})`,
        x.saved_amount ?? "0.00",
        "text",
        'inputmode="decimal" data-decimal min="0" max="9999999999.99" required',
      ) +
      field(
        "target_date",
        "Target date (optional)",
        x.target_date || "",
        "date",
        'min="1900-01-01" max="9998-12-31"',
        "Updating savings progress does not move money between your wallets.",
        true,
      );
  }
  if (type === "budget") {
    title = editing ? "Edit category limit" : "Set a category limit";
    description = "A little guidance for your everyday spending.";
    const available = state.data.categories.filter(
      (c) =>
        (c.kind === "expense" || c.kind === "both") &&
        (!state.data.budgets.some((b) => b.category === c.id) ||
          c.id === x.category),
    );
    if (!available.length) {
      showDialog(
        "Every category has a limit.",
        "Create a new expense category in Settings, or edit one of your existing limits.",
        `<div class="form-actions">${button("Done", "close-dialog", "", "btn-primary")}</div>`,
      );
      return;
    }
    content =
      selectField(
        "category",
        "Expense category",
        available.map((c) => ({ value: c.id, label: c.name })),
        x.category || available[0]?.id,
        "required",
        true,
      ) +
      field(
        "monthly_limit",
        `Monthly limit (${state.data.profile.currency})`,
        x.monthly_limit || "",
        "text",
        moneyAttrs,
        "This limit repeats every month. Spending is calculated for your selected reporting month.",
        true,
      );
  }
  if (type === "recurring") {
    title = editing ? "Edit recurring payment" : "Add a recurring payment";
    description = "Create a routine for your regular income or bills.";
    content =
      field(
        "title",
        "Payment name",
        x.title || "",
        "text",
        'maxlength="120" required placeholder="e.g. Monthly rent"',
        "",
        true,
      ) +
      selectField(
        "kind",
        "Type",
        [
          { value: "expense", label: "Expense" },
          { value: "income", label: "Income" },
        ],
        kind,
      ) +
      field(
        "amount",
        `Amount (${state.data.profile.currency})`,
        x.amount || "",
        "text",
        moneyAttrs,
      ) +
      selectField(
        "wallet",
        "Wallet",
        walletOptions(x.wallet),
        x.wallet || state.data.wallets.find((w) => w.is_active)?.id,
        "required",
      ) +
      selectField(
        "category",
        "Category",
        categoryOptions(kind, x.category),
        x.category || "",
      ) +
      field(
        "day_of_month",
        "Day of the month",
        x.day_of_month || "1",
        "number",
        'min="1" max="31" step="1" required',
        "Days 29–31 use the last day of shorter months.",
        true,
      ) +
      `<label class="checkbox-field full"><input name="is_active" type="checkbox" ${x.is_active !== false ? "checked" : ""}> Active payment</label>`;
  }
  if (type === "category") {
    title = editing ? "Edit category" : "Create a category";
    description = "A simple label to keep your records organized.";
    content =
      field(
        "name",
        "Category name",
        x.name || "",
        "text",
        'maxlength="80" required placeholder="e.g. Learning & books"',
        "",
        true,
      ) +
      selectField(
        "kind",
        "Use for",
        [
          { value: "expense", label: "Expenses" },
          { value: "income", label: "Income" },
          { value: "both", label: "Income and expenses" },
        ],
        x.kind || "expense",
        "",
        true,
      );
  }
  showDialog(
    title,
    description,
    `<form data-form="entity" data-type="${type}" ${editing ? `data-id="${num(x.id)}"` : ""}><div class="form-error dialog-error" role="alert"></div><div class="form-grid">${content}</div><div class="form-actions">${button("Cancel", "close-dialog", "", "btn-secondary")}<button type="submit" class="btn btn-primary">${icon("check", "small")}${editing ? "Save changes" : "Create " + (type === "budget" ? "limit" : type === "recurring" ? "payment" : type)}</button></div></form>`,
  );
}
function confirmDelete(type, id) {
  const item = findItem(collections[type], id);
  if (!item) return;
  const name = item.name || item.title || categoryName(item.category);
  let description = `This will permanently remove “${name}”.`;
  if (type === "transaction")
    description += " Your wallet balance and reports will update.";
  if (type === "wallet")
    description += " Wallets with activity must be archived instead.";
  if (type === "category")
    description += " Categories used in your records cannot be deleted.";
  showDialog(
    `Delete ${type === "budget" ? "limit" : type === "recurring" ? "payment" : type}?`,
    description,
    `<form data-form="delete" data-type="${type}" data-id="${num(id)}"><div class="form-error" role="alert"></div><div class="form-actions">${button("Keep it", "close-dialog", "", "btn-secondary")}<button class="btn btn-danger" type="submit">${icon("trash", "small")}Delete</button></div></form>`,
  );
}
function entityPayload(form) {
  const values = Object.fromEntries(new FormData(form)),
    type = form.dataset.type;
  form.querySelectorAll("[data-decimal]").forEach((input) => {
    if (input.name in values) values[input.name] = normalizeDecimal(values[input.name]);
  });
  for (const k of ["wallet", "category"])
    if (k in values) values[k] = values[k] === "" ? null : Number(values[k]);
  if ("day_of_month" in values)
    values.day_of_month = Number(values.day_of_month);
  if ("target_date" in values && !values.target_date) values.target_date = null;
  if (type === "wallet" && form.dataset.id)
    values.is_active = form.elements.is_active.checked;
  if (type === "recurring") values.is_active = form.elements.is_active.checked;
  return values;
}
function validateWallet(form) {
  const wallet = form.elements.wallet;
  if (wallet) {
    const w = findItem("wallets", wallet.value);
    wallet.setCustomValidity(
      w && !w.is_active
        ? "This wallet is archived. Restore it in Wallets, or choose an active wallet."
        : "",
    );
  }
  return form.reportValidity();
}
function validateDecimalInputs(form) {
  let valid = true;
  form.querySelectorAll("[data-decimal]").forEach((input) => {
    const value = parseDecimal(input.value);
    const min = input.min === "" ? -Infinity : Number(input.min);
    const max = input.max === "" ? Infinity : Number(input.max);
    const message = !Number.isFinite(value)
      ? state.locale === "pl" ? "Wpisz liczbę, na przykład 12,50." : "Enter a number, for example 12.50."
      : value < min || value > max
        ? state.locale === "pl" ? `Wpisz wartość od ${min} do ${max}.` : `Enter a value from ${min} to ${max}.`
        : "";
    input.setCustomValidity(message);
    if (message) valid = false;
  });
  return valid;
}
function setBusy(form, busy) {
  form.querySelectorAll("button[type=submit]").forEach((b) => {
    b.disabled = busy;
    b.setAttribute("aria-busy", String(busy));
  });
}
async function submitForm(form) {
  if (form.dataset.busy === "true") return;
  const name = form.dataset.form;
  if (name === "entity" && !validateWallet(form)) return;
  if (!validateDecimalInputs(form)) {
    form.reportValidity();
    return;
  }
  if (!form.reportValidity()) return;
  const payload = Object.fromEntries(new FormData(form));
  form.querySelectorAll("[data-decimal]").forEach((input) => {
    if (input.name in payload) payload[input.name] = normalizeDecimal(payload[input.name]);
  });
  if (
    name === "auth" &&
    state.authMode === "signup" &&
    payload.password !== payload.password_confirm
  ) {
    fieldErrors(
      form,
      new Error(
        "Your passwords do not match. Please enter the same password twice.",
      ),
    );
    return;
  }
  form.dataset.busy = "true";
  setBusy(form, true);
  form.querySelector(".form-error")?.replaceChildren();
  try {
    if (name === "auth") {
      const result = await api(
        state.authMode === "signup" ? "register" : "login",
        { method: "POST", body: payload },
      );
      state.session = { ...result, authenticated: true };
      state.route = "dashboard";
      history.replaceState({}, "", "/");
      await loadState();
      toast(
        state.authMode === "signup"
          ? "Your next chapter starts here. Welcome to FinanceFlow."
          : "Good to have you back.",
      );
    }
    if (name === "entity") {
      const type = form.dataset.type,
        id = form.dataset.id;
      await api(`${collections[type]}${id ? "/" + id : ""}`, {
        method: id ? "PATCH" : "POST",
        body: entityPayload(form),
      });
      closeDialog();
      await loadState({ quiet: true });
      toast(
        `${type === "budget" ? "Category limit" : type === "recurring" ? "Recurring payment" : type.charAt(0).toUpperCase() + type.slice(1)} ${id ? "updated" : "created"}.`,
      );
      document.querySelector("#page-title")?.focus({ preventScroll: true });
    }
    if (name === "delete") {
      await api(`${collections[form.dataset.type]}/${form.dataset.id}`, {
        method: "DELETE",
      });
      closeDialog();
      await loadState({ quiet: true });
      toast("Deleted. Your overview is up to date.");
      document.querySelector("#page-title")?.focus({ preventScroll: true });
    }
    if (name === "plan") {
      const total = ["essential_pct", "lifestyle_pct", "savings_pct"].reduce(
        (sum, key) => sum + Math.round(num(payload[key]) * 100),
        0,
      );
      if (total !== 10000)
        throw new Error("Your percentages must add up to exactly 100%.");
      await api("plan", { method: "PATCH", body: payload });
      await loadState({ quiet: true });
      toast("Your budget allocation is saved.");
    }
    if (name === "settings") {
      await api("settings", { method: "PATCH", body: payload });
      await loadState({ quiet: true });
      toast("Your preferences are saved.");
    }
    if (name === "coach") {
      const result = await api("coach", { method: "POST", body: payload });
      state.coachMessages.push(
        { role: "user", text: payload.message },
        { role: "assistant", text: result.reply },
      );
      document.querySelector("#coach-messages").innerHTML = coachMessages();
      form.reset();
      document.querySelector("#coach-message")?.focus();
    }
  } catch (err) {
    fieldErrors(form, err);
  } finally {
    form.dataset.busy = "false";
    setBusy(form, false);
  }
}
function closeNavigation() {
  document.querySelector("#sidebar")?.classList.remove("open");
  document
    .querySelector('[data-action="open-nav"]')
    ?.setAttribute("aria-expanded", "false");
}
async function handleAction(action, element) {
  const id = element.dataset.id;
  const entity = action.match(
    /^(add|edit|delete)-(transaction|wallet|goal|budget|recurring|category)$/,
  );
  if (entity) {
    if (entity[1] === "delete") confirmDelete(entity[2], id);
    else openEntity(entity[2], entity[1] === "edit" ? id : null);
    return;
  }
  if (action === "auth-switch") {
    state.authMode = state.authMode === "login" ? "signup" : "login";
    history.replaceState(
      {},
      "",
      state.authMode === "signup" ? "/signup/" : "/login/",
    );
    renderAuth();
  }
  if (action === "close-dialog") closeDialog();
  if (action === "dialog-add-wallet") {
    closeDialog();
    openEntity("wallet");
  }
  if (action === "open-nav") {
    document.querySelector("#sidebar")?.classList.add("open");
    element.setAttribute("aria-expanded", "true");
    document.querySelector(".mobile-close")?.focus();
  }
  if (action === "close-nav") {
    closeNavigation();
    document.querySelector('[data-action="open-nav"]')?.focus();
  }
  if (action === "logout") {
    element.disabled = true;
    try {
      const result = await api("logout", { method: "POST", body: {} });
      state.session = { ...result, authenticated: false, user: null };
      state.data = null;
      state.coachMessages = [];
      state.authMode = "login";
      history.replaceState({}, "", "/login/");
      renderAuth();
      toast("You have signed out. See you soon.");
    } catch (err) {
      toast(errorText(err), true);
      element.disabled = false;
    }
  }
  if (action === "reset-filters") {
    state.filters = { search: "", kind: "all", wallet: "all" };
    render();
  }
  if (action === "reset-plan") {
    for (const key of ["essential_pct", "lifestyle_pct", "savings_pct"])
      document.querySelector("#plan-form").elements[key].value =
        state.data.plan[key];
    updatePlanPreview();
  }
  if (action === "export") {
    const link = document.createElement("a");
    link.href = `/api/export?month=${encodeURIComponent(state.month)}`;
    link.download = `financeflow-${state.month}.csv`;
    document.body.append(link);
    link.click();
    link.remove();
  }
  if (action === "apply-recurring") {
    element.disabled = true;
    try {
      const result = await api("recurring/apply", {
        method: "POST",
        body: { month: state.month },
      });
      await loadState({ quiet: true });
      toast(
        result.created
          ? `${result.created} due payment${result.created === 1 ? "" : "s"} recorded.`
          : "You are up to date. No new payments are due.",
      );
    } catch (err) {
      toast(errorText(err), true);
    } finally {
      element.disabled = false;
    }
  }
}
document.addEventListener("click", (event) => {
  const route = event.target.closest("[data-route]");
  if (route) {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)
      return;
    event.preventDefault();
    navigate(route.dataset.route);
    return;
  }
  const action = event.target.closest("[data-action]");
  if (action && action.tagName === "BUTTON") {
    event.preventDefault();
    handleAction(action.dataset.action, action).catch((err) =>
      toast(errorText(err), true),
    );
  }
});
document.addEventListener("submit", (event) => {
  const form = event.target.closest("form[data-form]");
  if (form) {
    event.preventDefault();
    submitForm(form);
  }
});
document.addEventListener("input", (event) => {
  if (event.target.matches("[data-decimal]")) event.target.setCustomValidity("");
  if (event.target.id === "transaction-search") {
    state.filters.search = event.target.value;
    document.querySelector("#transaction-results").innerHTML =
      transactionResults(filteredTransactions());
  }
  if (event.target.closest("#plan-form") && event.target.matches("input"))
    updatePlanPreview();
});
document.addEventListener("change", async (event) => {
  const el = event.target;
  if (el.matches("[data-language]")) {
    state.locale = el.value === "pl" ? "pl" : "en";
    localStorage.setItem("financeflow-language", state.locale);
    render();
    return;
  }
  if (el.dataset.filter) {
    state.filters[el.dataset.filter] = el.value;
    document.querySelector("#transaction-results").innerHTML =
      transactionResults(filteredTransactions());
  }
  if (el.name === "month" && el.matches('[data-action="month"]')) {
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(el.value) || !el.validity.valid) return;
    const previous = state.month;
    state.month = el.value;
    try {
      await loadState();
    } catch (err) {
      state.month = previous;
      el.value = previous;
      toast(errorText(err), true);
    }
  }
  if (el.name === "kind" && el.closest('form[data-form="entity"]')) {
    const select = el.form.elements.category;
    if (select) {
      const previous = select.value;
      select.innerHTML = categoryOptions(el.value)
        .map((o) => `<option value="${esc(o.value)}">${esc(o.label)}</option>`)
        .join("");
      if ([...select.options].some((o) => o.value === previous))
        select.value = previous;
    }
  }
  if (el.name === "wallet" && el.form) el.setCustomValidity("");
});
document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    !dialog.open &&
    document.querySelector("#sidebar.open")
  ) {
    closeNavigation();
    document.querySelector('[data-action="open-nav"]')?.focus();
  }
  if (event.key === "Tab" && document.querySelector("#sidebar.open")) {
    const elements = [
      ...document.querySelectorAll("#sidebar button,#sidebar a"),
    ].filter((x) => x.getClientRects().length);
    const first = elements[0],
      last = elements.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
});
dialog.addEventListener("close", () => {
  if (state.dialogReturn?.isConnected)
    state.dialogReturn.focus({ preventScroll: true });
});
window.addEventListener("popstate", () => {
  state.route = currentRoute();
  if (!state.session?.authenticated)
    state.authMode = location.pathname.includes("signup") ? "signup" : "login";
  render();
});
async function boot() {
  try {
    state.session = await api("session");
    state.route = currentRoute();
    if (state.session.authenticated) await loadState({ quiet: true });
    else renderAuth();
  } catch (err) {
    app.innerHTML = `<main class="fatal-screen" id="main-content"><div class="brand"><span class="brand-mark">f.</span><span>FinanceFlow</span></div><h1>A little pause.</h1><p>${esc(errorText(err))}</p><button class="btn btn-primary" id="retry-boot">Try again</button></main>`;
    document.querySelector("#retry-boot").addEventListener("click", boot);
  }
}
boot();
