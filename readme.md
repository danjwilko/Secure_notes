# Secure Notes

Secure Notes is a security-focused Django web application for creating and managing personal notes with authenticated user access, REST API support, and JWT authentication.

The project was built to explore secure-by-design backend engineering concepts using Django and Django REST Framework, with a focus on authentication, access control, API security, testing, and secure configuration practices.

---

## Features

### Core Features

* User registration and authentication
* Create, edit, and delete personal notes
* User-scoped note ownership and isolation
* Markdown note rendering
* Responsive Bootstrap-based UI
* REST API access using Django REST Framework

### API Features

* JWT authentication using SimpleJWT
* Protected API endpoints
* Pagination support
* OpenAPI schema generation
* Interactive Swagger documentation

### Security Features

* User-scoped queryset filtering
* Owner-based access control
* JWT-protected API endpoints
* API throttling on authentication endpoints
* Markdown sanitisation using Bleach
* Database uniqueness constraints
* Environment variable configuration
* Production-aware security settings
* Permission and ownership API tests
* Invalid JWT handling tests
* Field-level encryption using django-fernet-encrypted-fields
* Encrypted note content at rest
* Encryption key material derived from Django `SECRET_KEY` and `SALT_KEY`

---

## Tech Stack

### Backend

* Python 3
* Django 6
* Django REST Framework

### Authentication & Security

* Django session authentication
* JWT authentication (SimpleJWT)
* Field-level encryption (django-fernet-encrypted-fields)
* Bleach sanitisation
* Django security middleware/settings

### Documentation

* drf-spectacular
* OpenAPI / Swagger

### Database

* SQLite (development)

### Testing

* Pytest
* pytest-django

---

## Running the Project Locally

Clone the repository:

```bash
git clone <repo-url>
cd secure-notes
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment configuration:

```bash
cp .env.example .env
```

Apply database migrations:

```bash
python manage.py migrate
```

(Optional) Create an admin account:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

---

## API Documentation

Interactive Swagger documentation:

```text
/api/docs/
```

OpenAPI schema:

```text
/api/schema/
```

Example endpoints:

```text
POST /api/token/
GET /api/notes/
POST /api/notes/
```

---

## Tests

Tests are implemented using pytest and Django’s test database.

Run the test suite with:

```bash
pytest
```

Current test coverage includes:

* JWT authentication tests
* Invalid token handling
* CRUD API tests
* Ownership and permission tests
* Partial update tests
* Duplicate title validation tests
* Cross-user access protection tests

---

## Project Goals

This project focuses on exploring practical backend engineering concepts including:

* Secure authentication flows
* User-scoped data isolation
* REST API architecture
* Backend testing practices
* Secure configuration handling
* Defensive backend design
* API security concepts
* Production-aware Django configuration

---

## Roadmap

### Short-Term

* README and architecture documentation improvements
* Production deployment configuration
* Security header review
* Additional edge-case testing
* CI/CD pipeline setup

### Mid-Term

* Full-text search
* Tags/categories
* Export functionality
* Audit logging
* PostgreSQL deployment

### Advanced Exploration

* KEK/DEK experimentation
* Zero-knowledge architecture research
* Client-side encryption experiments
* Separate frontend/API-only architecture

---

## Disclaimer

This project is intended as a learning and portfolio project focused on backend engineering and security-oriented development practices. It is not currently intended for production use without additional deployment hardening and operational review.
