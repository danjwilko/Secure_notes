# Secure Notes

A security-focused Django web application for creating and managing personal notes.

## Why This Project?

Secure Notes began as a personal learning project to explore backend engineering and security-focused development using Django.

The goal was to create something small and practical that could be used to develop my Python and Django knowledge, while also becoming a genuinely useful application as the project evolved. A notes application filled that role well, as it was usable from almost day one.

The project follows a “do a few things well” philosophy. Rather than continuously adding features, the focus has been on improving architecture, security, testing and deployment while keeping the application simple enough to fully understand and reason about.

As a result, Secure Notes now serves both as a useful personal application and as a portfolio project demonstrating backend engineering and secure-by-design development principles.

## Live Demo

https://securenotes-production.up.railway.app

> Note: This application is a portfolio and learning project. Do not store sensitive real-world information.

---

## Architecture overview

The application uses a hybrid Django architecture:

- Traditional Django templates for the web interface
- Django REST Framework for API endpoints
- Session authentication for browser access
- JWT authentication for API access
- PostgreSQL as the primary database
- Field-level encryption for note content

Notes are always scoped to the authenticated user through queryset filtering and ownership enforcement at the API layer.

---

## Features

### Core application

- User registration, authentication and session management
- Password change and password reset workflows
- Account deletion
- Create, edit and delete personal notes
- Markdown rendering with sanitisation
- Responsive Bootstrap UI

### API

- Full REST API via Django REST Framework
- JWT authentication with refresh token rotation and blacklisting
- Owner scoped queryset filtering on all endpoints
- Pagination and partial update (PATCH) support
- OpenAPI schema generation and interactive Swagger documentation

### Security

- Field-level encryption at rest using Fernet
- Encryption key material derived from `SECRET_KEY` and `SALT_KEY`
- User-scoped queryset filtering
- Owner automatically assigned on creation
- JWT access tokens short-lived (5 minutes)
- Refresh token rotation and blacklisting
- API throttling on authentication and API endpoints
- Markdown sanitisation via Bleach
- Database uniqueness constraints per user
- CSRF protection for session-authenticated views
- Environment-variable based secret management
- Production-aware settings separation

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 6, Django REST Framework |
| Authentication | Django sessions, SimpleJWT (JWT) |
| Encryption | django-fernet-encrypted-fields, Fernet symmetric encryption |
| Sanitisation | Bleach |
| API documentation | drf-spectacular, OpenAPI/Swagger |
| Database | PostgreSQL |
| Testing | Pytest, pytest-django |

---

## Deployment

The application is deployed to Railway and uses PostgreSQL as the production database.

### Production stack

- Railway
- PostgreSQL
- Gunicorn
- WhiteNoise
- Environment-based configuration

### Production configuration

- `DEBUG=False`
- Environment-managed secrets
- PostgreSQL database backend
- Static asset serving via WhiteNoise
- CSRF trusted origins configured
- Secure cookie and host configuration

The live deployment is intended for demonstration and portfolio purposes.

## Running locally

Clone the repository:

```bash
git clone <repo-url>
cd secure-notes
```

Create and activate a virtual environment:

```bash
python -m venv sn_env
source sn_env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment configuration:

```bash
cp .env.example .env
```

Edit `.env` and set your values — see `.env.example` for required keys.

Apply database migrations:

```bash
python manage.py migrate
```

Create an admin account (optional):

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

> **Note:** PostgreSQL is required.

---

## Environment variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `SALT_KEY` | Salt used in encryption key derivation |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host (default: `localhost`) |
| `DB_PORT` | Database port (default: `5432`) |

---

## API documentation

With the server running, interactive Swagger docs are available at:

```
/api/docs/
```

OpenAPI schema:

```
/api/schema/
```

Key endpoints:

```
POST   /api/token/           Obtain JWT access and refresh tokens
POST   /api/token/refresh/   Refresh access token
GET    /api/notes/           List notes (authenticated user only)
POST   /api/notes/           Create a note
GET    /api/notes/{id}/      Retrieve a note
PATCH  /api/notes/{id}/      Partial update
DELETE /api/notes/{id}/      Delete a note
```

---

## Tests

Run the full test suite:

```bash
pytest
```

Test coverage includes:

- JWT authentication and token lifecycle
- Invalid and expired token handling
- CRUD operations via API
- Ownership isolation (users cannot access other users' notes)
- Permission and access control
- Partial update (PATCH) behaviour
- Duplicate title validation per user
- Cross-user same-title isolation
- Malformed request handling
- Large input handling
- Markdown rendering and sanitisation
- API throttling
- Password change workflow
- Password reset workflow

---

## Roadmap

### Phase 1 Final polish

- Structured audit logging
- Consistent exception handling
- Security header review
- End-to-end integration testing
- Documentation improvements

### Phase 2 - Features and expansion

- Tags and categories
- Search functionality
- Export (JSON and Markdown)
- UX improvements and notifications

### Phase 3 - Engineering Depth

- CI/CD with GitHub Actions
- Docker and docker-compose
- Automated deployment pipeline
- Monitoring and health checks

### Phase 4 - Advanced security research

- KEK/DEK encryption architecture exploration
- Client-side encryption prototype
- Zero-knowledge architecture research 
- Separate React/Svelte frontend

---

## Disclaimer

This project was built as a learning and portfolio project focused on backend engineering and security-oriented development.

While deployed publicly for demonstration purposes, it has not undergone a formal security review and should not be considered suitable for storing sensitive real-world information.