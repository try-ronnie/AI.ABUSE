# Project Structure

```
backend/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── .requirements.txt             # Python dependencies
├── readme.md                     # Project documentation
│
├── alembic/                      # Database migrations
│   ├── alembic.ini               # Alembic configuration
│   ├── env.py                    # Alembic environment setup
│   └── versions/                 # Migration version files
│
└── app/                          # Main application package
    ├── main.py                   # Application entry point
    │
    ├── api/                      # API layer
    │   ├── deps.py               # Dependency injection
    │   └── v1/                   # API version 1 endpoints
    │       ├── animals.py        # Animal endpoints
    │       ├── auth.py           # Authentication endpoints
    │       ├── cart.py           # Shopping cart endpoints
    │       ├── orders.py         # Order endpoints
    │       ├── payments.py       # Payment endpoints
    │       └── users.py          # User endpoints
    │
    ├── core/                     # Core configuration
    │   ├── __init__.py
    │   ├── config.py             # Application settings
    │   ├── database.py           # Database connection
    │   └── security.py           # Security utilities (JWT, hashing)
    │
    ├── models/                   # SQLAlchemy ORM models
    │   ├── __init__.py
    │   ├── animal.py             # Animal model
    │   ├── cart.py               # Cart model
    │   ├── order.py              # Order model
    │   ├── payment.py            # Payment model
    │   └── user.py               # User model
    │
    ├── schemas/                  # Pydantic schemas
    │   ├── __init__.py
    │   ├── animal.py             # Animal schemas
    │   ├── auth.py               # Authentication schemas
    │   ├── cart.py               # Cart schemas
    │   ├── order.py              # Order schemas
    │   ├── payment.py            # Payment schemas
    │   └── user.py               # User schemas
    │
    └── services/                 # Business logic layer
        ├── __init__.py
        ├── animal_service.py     # Animal business logic
        ├── cart_service.py       # Cart business logic
        ├── order_service.py      # Order business logic
        └── payment_service.py    # Payment business logic
```

## Architecture Overview

This project follows a **layered architecture** pattern:

1. **API Layer** (`api/`) - Handles HTTP requests/responses and routing
2. **Schemas Layer** (`schemas/`) - Data validation and serialization using Pydantic
3. **Services Layer** (`services/`) - Business logic and orchestration
4. **Models Layer** (`models/`) - Database ORM models using SQLAlchemy
5. **Core Layer** (`core/`) - Shared configuration, database, and security utilities

## Key Technologies

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation and settings management
