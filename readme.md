# Secure Notes

A security-focused Django web application for creating and managing personal notes.

The project was built to explore backend engineering and security-focused development practices using Django and Django REST Framework, with a focus on authentication, access control, API security, encryption-at-rest, testing and production-aware configuration.

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

- Field level encryption at rest using Fernet (note content encrypted in the database)
- Encryption key material derived from `SECRET_KEY` and `SALT_KEY`
- User scoped queryset filtering (users can only access their own notes)
- Owner automatically assigned on creation (not trusted from client input)
- JWT access tokens short-lived (5 minutes); refresh tokens rotate on use and are blacklisted after rotation
- API throttling on authentication and general endpoints
- Markdown sanitisation via Bleach to reduce XSS risk from user content
- Database uniqueness constraints per user
- Environment variable configuration via `.env`

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

> **Note:** PostgreSQL is required. See [`docs/postgres-fedora-setup.md`](docs/postgres-fedora-setup.md) for a full setup walkthrough including common errors.

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
- Permission and access control edge cases
- Partial update (PATCH) behaviour
- Duplicate title validation per user
- Cross-user same-title isolation
- Malformed request handling
- Large input handling
- Markdown rendering
- API throttling

---

## Development and Security notes

The `docs/` folder contains working implementation notes and security-related development writeups created during the build process. Some documents are still being expanded and refined as the project evolves.

- [`docs/jwt-implementation.md`](docs/jwt-implementation.md) - JWT design decisions and token lifecycle
- [`docs/api-throttling.md`](docs/api-throttling.md) - Throttling approach and configuration
- [`docs/markdown-sanitisation.md`](docs/markdown-sanitisation.md) Bleach allowlist approach and XSS prevention
- [`docs/application-hardening.md`](docs/application-hardening.md) - Queryset filtering, IDOR prevention, and the authentication vs authorisation distinction
- [`docs/postgres-fedora-setup.md`](docs/postgres-fedora-setup.md) - PostgreSQL setup walkthrough for Fedora

---

## Roadmap

### Current focus (Phase 1 - portfolio polish)

- README and architecture documentation
- Production security settings review
- Security headers
- End-to-end golden path test
- `.env.example` and project hygiene

### Next (Phase 2 - feature expansion)

- Tags and categories
- Export (JSON and Markdown)
- Toast notifications and UX improvements

### Engineering depth (Phase 3)

- Audit logging (login, note events, failed auth)
- CI/CD via GitHub Actions
- Docker and docker-compose
- Production deployment

### Research track (Phase 4)

- KEK/DEK encryption architecture exploration
- Zero-knowledge prototype with WebCrypto and Argon2id
- Client-side encryption research
- Separate frontend (React or Svelte)

---

## Disclaimer

This project is a learning and portfolio project focused on backend engineering and security-oriented development. It is not intended for production use without additional deployment hardening and operational review.
