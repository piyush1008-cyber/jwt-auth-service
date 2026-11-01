# 🔐 Production JWT Authentication & Role-Based Access Control (RBAC) API

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-RFC%207519-black?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Security](https://img.shields.io/badge/Security-bcrypt%20Salted-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-7%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **An enterprise-grade, stateless authentication microservice implementing OAuth2 password flow, cryptographic JWT signatures, refresh token rotation with replay prevention, and granular Role-Based Access Control (RBAC).**

---

## 🛡️ Authentication & Token Lifecycle Workflow

```
[ Client ]                        [ Auth Service ]                        [ Database ]
    |                                    |                                     |
    |---- 1. POST /api/v1/auth/login --->|                                     |
    |     (username + password)          |---- 2. Query user & verify bcrypt ->|
    |                                    |<--- User record valid --------------|
    |                                    |                                     |
    |                                    |---- 3. Store Refresh Token -------->|
    |<--- 4. Return (Access + Refresh) --|                                     |
    |                                    |                                     |
    |---- 5. GET /api/v1/users/me ------>|                                     |
    |     Header: Bearer <access_token>  | (Stateless signature verification)  |
    |<--- 6. Return User Profile --------|                                     |
    |                                    |                                     |
    |---- 7. POST /api/v1/auth/refresh ->|                                     |
    |     (refresh_token)                |---- 8. Invalidate old token ------->|
    |                                    |---- 9. Store new refresh token ---->|
    |<--- 10. Return fresh token pair ---|                                     |
```

---

## 🚀 Key Security Features

- 🔑 **Cryptographic JWT Signing:** Standard RFC 7519 tokens signed with HMAC-SHA256 (`HS256`) and unique `jti` nonces.
- 🔒 **Bcrypt Salted Password Hashing:** 12 work-factor rounds with unique per-user salts preventing rainbow table attacks.
- 🔄 **Refresh Token Rotation (RTR):** Automatically revokes old refresh tokens upon renewal, defeating token replay and theft.
- 👥 **Role-Based Access Control (RBAC):** Hierarchical permissions (`user`, `moderator`, `admin`) enforced via FastAPI dependency injection.
- ⚡ **Stateless Authorization:** Authenticates requests in sub-millisecond time without per-request database lookups for session validation.
- 🧪 **Automated Test Coverage:** Complete Pytest test suite covering registration, bad credentials, forbidden roles, and token rotation.
- 🐳 **Dockerized:** Ready for instant container deployment with multi-stage build.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | FastAPI | Asynchronous high-speed Python REST framework |
| **Language** | Python 3.12 | Strongly typed, modern Python |
| **Token Specification** | PyJWT | RFC 7519 JSON Web Token signing & validation |
| **Hashing Engine** | bcrypt | Adaptive password hashing with cryptographic salt |
| **ORM / Storage** | SQLAlchemy 2.0 / SQLite | Relational database modeling & token persistence |
| **Testing** | Pytest + Starlette TestClient | In-memory unit and integration tests |

---

## 📁 Repository Structure

```
jwt-auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entrypoint & CORS
│   ├── config.py            # Security & cryptographic settings
│   ├── database.py          # SQLAlchemy engine & session dependency
│   ├── models.py            # User and RefreshToken ORM models
│   ├── schemas.py           # Pydantic v2 validation contracts
│   ├── security.py          # Password hashing & JWT generation/decoding
│   ├── dependencies.py      # OAuth2 Bearer & RBAC role guards
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /register, /login, /refresh, /logout
│       ├── users.py         # /users/me
│       └── admin.py         # /admin/users, /admin/stats
├── tests/
│   ├── __init__.py
│   └── test_auth.py         # Pytest verification suite (7 tests)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Quickstart Guide

### 1. Clone & Set Up Locally

```bash
git clone https://github.com/piyush1008-cyber/jwt-auth-service.git
cd jwt-auth-service

python -m venv venv
venv\Scripts\activate       # On Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation available at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Run with Docker

```bash
docker-compose up --build -d
```

---

## 📡 API Reference & Examples

### 1. Register Account
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "peeyoosh@example.com", "username": "peeyoosh", "password": "Password123!", "role": "admin"}'
```

### 2. Login & Acquire Tokens
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username_or_email": "peeyoosh", "password": "Password123!"}'
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 30
}
```

### 3. Access Protected Route
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 4. Admin-Only Endpoint (RBAC Enforced)
```bash
curl -X GET "http://localhost:8000/api/v1/admin/stats" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 🧪 Automated Testing

```bash
pytest -v
```

Expected output:
```text
tests/test_auth.py::test_health_and_root PASSED                          [ 14%]
tests/test_auth.py::test_register_and_login_flow PASSED                  [ 28%]
tests/test_auth.py::test_duplicate_registration_prevented PASSED         [ 42%]
tests/test_auth.py::test_invalid_login_credentials PASSED                [ 57%]
tests/test_auth.py::test_unauthorized_access_without_token PASSED        [ 71%]
tests/test_auth.py::test_role_based_access_control PASSED                [ 85%]
tests/test_auth.py::test_refresh_token_rotation PASSED                   [100%]

============================== 7 passed in 3.12s ==============================
```

---

## 👤 Author

**Peeyoosh Kangle**
- 📧 Email: piyushkangle@gmail.com
- 🐙 GitHub: [github.com/piyush1008-cyber](https://github.com/piyush1008-cyber)

---

## 📄 License

This repository is distributed under the MIT License — see the [LICENSE](LICENSE) file.
