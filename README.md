# Django + React JWT Authentication System

A full authentication system: registration with email OTP verification,
login, JWT access/refresh tokens stored in **HTTP-only cookies** (never in
`localStorage`/`sessionStorage`), a protected dashboard, token refresh, and
logout.

```
project/
├── backend/     Django + DRF API
├── frontend/    React (Vite) SPA
└── docs/        API docs + Postman collection
```

## Tech stack

- Django 5 + Django REST Framework
- djangorestframework-simplejwt (with token blacklist app for logout/rotation)
- django-cors-headers
- React 18 + Vite + React Router + Axios

## How auth works here

- On register, the user is created **inactive** and a 6-digit OTP (5-minute
  expiry) is emailed.
- The account is activated only after OTP verification.
- Login is blocked until the account is verified.
- On login, the backend issues a JWT access token (15 min) and refresh token
  (7 days) and sets them as `httponly`, `samesite=Lax` cookies — JavaScript
  on the frontend never touches the raw tokens.
- A custom DRF authentication class (`accounts/authentication.py`) reads the
  `access_token` cookie instead of the `Authorization` header.
- `POST /api/token/refresh/` reads the `refresh_token` cookie and rotates
  both tokens (old refresh token is blacklisted).
- The frontend's axios instance automatically retries a request once via
  `/api/token/refresh/` if it gets a `401`, so the user experience is
  seamless while the access token is short-lived.

See `docs/API_DOCUMENTATION.md` for full endpoint details and
`docs/postman_collection.json` for a ready-to-import Postman collection.

---

## 1. Backend setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows: venv\Scripts\activate
or
source venv/bin/activate        # other OS

pip install -r requirements.txt

cp .env.example .env            # edit values as needed (see below)

python manage.py migrate # if errors then python manage.py makemigrations accounts and python manage.py makemigrations
python manage.py createsuperuser   # optional, for /admin/

python manage.py runserver         # http://localhost:8000
```

### Environment variables (`backend/.env`)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True`/`False` |
| `FRONTEND_URL` | Origin allowed by CORS, e.g. `http://localhost:5173` |
| `EMAIL_BACKEND` | Use `django.core.mail.backends.console.EmailBackend` for local dev — OTP emails print to the terminal. Switch to `django.core.mail.backends.smtp.EmailBackend` for real emails. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP credentials (only needed with the SMTP backend, e.g. Gmail app password) |
| `COOKIE_SECURE` | Set `True` in production (HTTPS only) |
| `COOKIE_SAMESITE` | `Lax` for local dev; consider `None` (+ `Secure=True`) if frontend/backend are on different domains in production |

With the console email backend (the default), just watch the terminal
running `runserver` — the OTP will be printed there after registering.

---

## 2. Frontend setup

```bash
cd frontend
npm install

cp .env.example .env    # VITE_API_URL=http://localhost:8000/api

npm run dev              # http://localhost:5173
```

---

## 3. Try the flow

1. Start the backend (`:8000`) and frontend (`:5173`).
2. Open `http://localhost:5173/register`, fill the form.
3. Check the backend terminal for the printed OTP email (or your inbox, if
   SMTP is configured).
4. Enter the email + OTP on the verify page.
5. Log in — you're redirected to the protected `/dashboard`, which shows
   your name, email, and verification status.
6. Refresh the page — the session persists because the JWTs live in
   HTTP-only cookies and `/api/profile/` is called on load.
7. Click **Logout** — cookies are cleared and you're redirected to login.

---

## Notes / production considerations

- SQLite is used for simplicity; swap `DATABASES` in `backend/config/settings.py`
  for Postgres/MySQL in production.
- If frontend and backend are deployed on different domains, set
  `COOKIE_SAMESITE=None` and `COOKIE_SECURE=True` (requires HTTPS) so
  cross-site cookies are sent.
- CSRF: since JWT cookie auth (not Django session auth) is used for the API,
  DRF's `SessionAuthentication` is not in `DEFAULT_AUTHENTICATION_CLASSES`,
  so CSRF tokens are not required for these endpoints.
- Consider rate-limiting `/api/register/`, `/api/login/`, and
  `/api/resend-otp/` in production to prevent abuse (e.g. `django-ratelimit`
  or DRF throttling classes).
