# FastAPI Backend with PostgreSQL

A modern REST API built with FastAPI and PostgreSQL for backend development.

## Features

- FastAPI for high-performance async web APIs
- PostgreSQL database with SQLAlchemy ORM
- Docker containerization
- Environment-based configuration
- Modular API structure

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application instance
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database connection and session management
│   ├── config.py            # Application configuration
│   ├── exceptions.py        # Custom exception classes
│   ├── middleware.py        # Custom middleware functions
│   ├── api/
│   │   ├── __init__.py
│   │   └── users.py         # User-related API endpoints
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication utilities (JWT, password hashing)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic models for request/response validation
│   ├── services/
│   │   ├── __init__.py
│   │   └── user.py          # Business logic and CRUD operations
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py        # Logging utilities
│   └── tests/
│       ├── __init__.py
│       └── test_users.py    # Unit tests for user functionality
├── alembic/                 # Database migration scripts
├── scripts/
│   ├── __init__.py
│   └── init_db.py           # Database initialization script
├── docs/
│   └── api.md               # API documentation
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
├── Makefile                 # Common commands
├── .env                     # Environment variables
├── .gitignore               # Git ignore rules
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Multi-container setup
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if running locally)

### Local Development

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd kiki
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env` and update the values as needed.

5. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at <http://localhost:8000>

### Using Docker

1. Build and run with Docker Compose:

   ```bash
   docker-compose up --build
   ```

   This will start both the FastAPI app and PostgreSQL database.

2. Access the API at <http://localhost:8000>

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info (requires authentication)

### Users

- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users/` - Create a new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### General

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

For detailed API documentation, see [docs/api.md](docs/api.md).

## Database

The application uses PostgreSQL with SQLAlchemy ORM. Database tables are created automatically on startup.

## Testing

Run tests with:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
