# Bayzid — Marketplace Foundation

**Bayzid** ("Shop • Sell • Earn") is a multi-vendor e-commerce marketplace: buyers shop,
sellers list and manage products, and affiliates earn commission by sharing product links.

This repository is the **real, runnable foundation** of that platform — not a static
mockup. Steps 1–2 (project architecture + Django backend + auth flow + homepage) are
complete; the remaining build steps continue from here (see "Roadmap" below).

## Stack

- **Backend:** Python, Django 5, Django REST Framework, PostgreSQL, SimpleJWT
- **Frontend:** HTML5, Tailwind CSS (CDN), vanilla JavaScript — no framework
- **Auth:** Email/phone login, JWT access + refresh tokens, 6-digit OTP (email now,
  SMS-ready), password reset flow
- **Money:** All financial fields use `Decimal`, never floats

## Project Structure

```
bayzid/
├── backend/
│   ├── manage.py
│   ├── config/            settings, urls, wsgi/asgi
│   ├── accounts/          User, Profile, Address, OTP, auth APIs
│   ├── products/          Category, Product, ProductImage, ProductVariant
│   ├── orders/             Cart, CartItem, Wishlist, Order, OrderItem, Coupon, checkout
│   ├── sellers/            SellerProfile, Store
│   ├── affiliates/         AffiliateProfile, AffiliateLink, AffiliateClick, AffiliateCommission
│   ├── wallet/              Wallet, WalletTransaction, Withdrawal
│   ├── payments/            Payment (bKash/Nagad/Card/COD-ready)
│   ├── reviews/             Review (verified-purchase only)
│   ├── notifications/       Notification, Banner
│   └── core/                 shared BaseModel (UUID pk), permissions
├── frontend/
│   ├── index.html, login.html, register.html, forgot-password.html, otp.html
│   ├── assets/logos/       your uploaded Bayzid logos
│   ├── css/style.css        Bayzid design tokens (navy #1E3A8A / orange #F97316)
│   └── js/                  api.js (fetch + JWT client), ui.js (toasts, OTP inputs, etc.)
├── .env.example
├── requirements.txt
├── docker-compose.yml       Postgres + Django, one command to run both
└── backend/Dockerfile
```

## Running it locally

### 1. Backend

```bash
cd bayzid
cp .env.example .env          # edit values as needed
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Requires a local PostgreSQL running with the credentials in .env
# (or use `docker compose up db` to start just the database)

cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API is now live at `http://localhost:8000/api/v1/` and Django admin at `/admin/`.

### 2. Or run everything with Docker

```bash
docker compose up --build
```

### 3. Frontend

The frontend is plain static HTML/CSS/JS — no build step. Serve it with any static
server, e.g.:

```bash
cd frontend
python -m http.server 5500
```

Then open `http://localhost:5500/index.html`. Update `CORS_ALLOWED_ORIGINS` in `.env`
to match whatever port you serve the frontend on.

If you're deploying (not just running locally), set `window.BAYZID_API_BASE_URL` in a
small inline script before `api.js` loads, pointing at your deployed backend URL.

## Security notes

- No secrets are committed. `.env.example` lists every variable the app needs —
  copy it to `.env` and fill in real values yourself for SMS/bKash/Nagad/email.
- Commission and pricing are **always calculated server-side** (see
  `affiliates/models.py::record_commission_for_order_item` and
  `orders/views.py::CheckoutView`) — the frontend never sends a trusted amount.
- JWT access tokens are short-lived (30 min) with rotating refresh tokens.

## Roadmap (matches the original 16-step plan)

- [x] Step 1 — Project architecture
- [x] Step 2 — Django backend foundation (all 10 apps, models, admin, core auth/OTP APIs)
- [x] Step 4 (partial) — Authentication APIs (register, login, OTP, password reset)
- [x] Step 5 — Frontend authentication pages (login, register, forgot password, OTP)
- [x] Step 6 (partial) — Homepage
- [ ] Step 7 — Product listing & product details pages
- [ ] Step 8 — Cart & checkout pages (backend APIs already exist in `orders/`)
- [ ] Step 9 — Buyer dashboard
- [ ] Step 10 — Seller dashboard
- [ ] Step 11 — Affiliate dashboard UI (backend APIs already exist in `affiliates/`)
- [ ] Step 12 — Wallet & withdrawal UI (backend APIs already exist in `wallet/`)
- [ ] Step 13 — Admin dashboard UI (Django admin is functional today; a branded
      custom dashboard is a later layer on top)
- [ ] Step 15 — Deeper validation, rate limiting tuning, production hardening pass
