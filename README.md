# Smart Yoram Backend

Smart Yoram (스마트 교회요람) Backend API service built with FastAPI.

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/            # API endpoints
├── core/           # Core configuration and security
├── db/             # Database configuration
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
└── services/       # Business logic
```

## Testing

```bash
pytest
```

## Code Quality

```bash
# Format code
black .

# Lint code
flake8

# Sort imports
isort .
```