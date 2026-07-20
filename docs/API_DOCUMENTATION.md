# API Documentation

Base URL (local development): `http://localhost:8000/api`

All requests/responses use `application/json`. Authenticated endpoints rely on
an `access_token` HTTP-only cookie (no `Authorization` header needed from the
browser) — make sure requests are sent with credentials/cookies included
(`withCredentials: true` in axios, or `credentials: "include"` in fetch).

---

## 1. Register

`POST /api/register/`

**Body**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "StrongPass123",
  "confirm_password": "StrongPass123"
}
```

**Response `201 Created`**
```json
{
  "message": "Registration successful. An OTP has been sent to your email.",
  "email": "jane@example.com"
}
```

**Errors `400`** — e.g. `{"email": ["A user with this email already exists."]}`

---

## 2. Verify OTP

`POST /api/verify-otp/`

**Body**
```json
{
  "email": "jane@example.com",
  "otp": "123456"
}
```

**Response `200 OK`**
```json
{ "message": "Email verified successfully. You can now log in." }
```

**Errors `400`** — invalid/expired OTP, e.g. `{"otp": ["OTP has expired. Please request a new one."]}`

OTPs expire **5 minutes** after they are generated.

---

## 3. Resend OTP

`POST /api/resend-otp/`

**Body**
```json
{ "email": "jane@example.com" }
```

**Response `200 OK`**
```json
{ "message": "A new OTP has been sent to your email." }
```

Generating a new OTP invalidates any previous unused OTP for that user.

---

## 4. Login

`POST /api/login/`

**Body**
```json
{
  "email": "jane@example.com",
  "password": "StrongPass123"
}
```

**Response `200 OK`**
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "is_verified": true,
    "date_joined": "2026-07-20T10:00:00Z"
  }
}
```

On success, the server sets two **HTTP-only cookies**:
- `access_token` (short-lived, 15 minutes)
- `refresh_token` (long-lived, 7 days)

Login is rejected with `400` if the account has not completed OTP
verification yet.

---

## 5. Refresh Access Token

`POST /api/token/refresh/`

No request body needed — the `refresh_token` cookie is read automatically.

**Response `200 OK`**
```json
{ "message": "Token refreshed." }
```
Sets a new `access_token` cookie (and a rotated `refresh_token` cookie, since
refresh token rotation + blacklisting is enabled).

**Errors `401`** if the refresh token is missing, invalid, expired, or
blacklisted.

---

## 6. Get Profile (protected)

`GET /api/profile/`

Requires a valid `access_token` cookie.

**Response `200 OK`**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "is_verified": true,
  "date_joined": "2026-07-20T10:00:00Z"
}
```

**Errors `401`** if not authenticated — the frontend should attempt
`/api/token/refresh/` and retry once before redirecting to login.

---

## 7. Logout

`POST /api/logout/`

Requires a valid `access_token` cookie.

**Response `200 OK`**
```json
{ "message": "Logged out successfully." }
```

Blacklists the refresh token and deletes both the `access_token` and
`refresh_token` cookies.

---

## Error format

Validation errors from DRF serializers are returned as `400` with a
field-keyed object, e.g.:
```json
{ "password": ["This password is too short."] }
```
Non-field errors (e.g. bad login credentials) appear under `non_field_errors`.

## Full flow

```
POST /api/register/         → user created (inactive), OTP emailed
POST /api/verify-otp/       → user activated + verified
POST /api/login/            → cookies set: access_token, refresh_token
GET  /api/profile/          → returns user info (cookie-authenticated)
POST /api/token/refresh/    → refreshes access_token when it expires
POST /api/logout/           → clears cookies, blacklists refresh token
```
