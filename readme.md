# Secure Notes

A secure Django-based notes application with user scoped data, REST API access and JWT authentication.

## Overview

Secure Notes is a Django web application that allows authenticated users to create and manage personal notes.

The project was built as a learning exercise to explore secure-by-design backend development using Django and the Django REST Framework, focusing on authentication, access control, and API design.

## Features

- User registration and authentication
- Personal note creation, editing, and deletion
- Notes scoped to the authenticated user
- REST API for notes using Django REST Framework
- JWT authentication for API access
- API throttling to reduce abuse (planned)

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework

### Authentication

- Django session authentication (web interface)
- JWT authentication (API access)

### Database

- SQLite (development)

### Tests

- Pytest
- Django ORM test database

## Security Considerations

- Notes restricted to the authenticated user
- API endpoints require JWT authentication
- Querysets filtered by request user
- Rate limiting on authentication endpoints
- Audit logging for note operations(planned)

## Running the project locally

    git clone <repo>
    cd secure-notes

    python -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt

    python manage.py migrate
    python manage.py runserver

## API Usage

The API allows programattic access to the notes using JWT authentication.

Example endpoints:

    POST /api/token/
    GET /api/notes/
    POST /api/notes/

## Testing

Tests are implemented using pytest and Django's test database.

Run tests with: 
    pytest

## Documentation

Additional design documentation is available in the '/docs' directory

## Roadmap

To be finalised.

## Learning Goals

The project was built to continue solidifying python knowledge and Django basics while exploring:

- Django application architecture.
- REST API development with the Django Rest Framework.
- Authentication and authorisation patterns.
- Secure handling of user-scoped data.
- Backend testing using pytest.
