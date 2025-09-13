# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database Operations
```bash
# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Initialize daily verses data
python run_daily_verse_migration.py
```

### Development Server
```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start with Docker Compose (includes Redis, Celery)
docker-compose up --build

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.core.celery_app beat --loglevel=info
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8

# Sort imports
isort .
```

### Testing
```bash
# Run tests
pytest

# Test specific endpoint
python test_api_endpoints.py
```

## Architecture Overview

Smart Yoram is a church management system with AI agent capabilities built on FastAPI. The system supports multi-tenancy for multiple churches with the following core components:

### Core Systems
1. **AI Agent Management** - Church-specific AI agents with customizable system prompts
2. **Chat System** - Real-time AI conversations with history management
3. **Church Database Integration** - Connection to external church databases for data queries
4. **Multi-tenant Support** - Isolated data per church organization
5. **Push Notifications** - Firebase-based notification system
6. **Member Management** - Enhanced member profiles with family relationships

### Database Architecture
- **Primary DB**: PostgreSQL with Supabase
- **Cache**: Redis for session management and background tasks
- **Task Queue**: Celery for async operations
- **External DB**: Configurable connections to church-specific databases (MySQL/PostgreSQL/MSSQL)

### Key Models
- `churches` - Church organizations with GPT API keys and subscription plans
- `ai_agents` - Custom AI agents per church with system prompts
- `chat_histories` & `chat_messages` - Conversation management
- `users` & `members` - User authentication and member profiles
- `push_notifications` & `user_devices` - Notification system
- `community_*` - Community features (sharing, requests, job posts, music teams)
- `church_events` - Church event management and announcements
- `music_team_recruitment` - Music team recruitment with relationship to users

## Project Structure

```
app/
├── api/api_v1/endpoints/    # API route handlers
├── core/                    # Configuration, security, Celery
├── models/                  # SQLAlchemy database models
├── schemas/                 # Pydantic request/response schemas
├── services/                # Business logic (OpenAI, push notifications)
├── crud/                    # Database operations
├── db/                      # Database configuration and initialization
└── utils/                   # Utilities (encryption, QR codes, email, etc.)
```

### Critical Services
- `openai_service.py` - GPT API integration with church context
- `church_data_service.py` - External database query management
- `push_notification.py` - Firebase messaging service
- `smart_assistant_service.py` - AI assistant integration for church operations

## Important Configuration

### Environment Variables
Required environment variables in `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` & `SUPABASE_ANON_KEY` - Supabase configuration
- `SECRET_KEY` - JWT token encryption
- `REDIS_URL` - Redis connection for Celery
- `FIREBASE_CREDENTIALS_PATH` - Firebase service account JSON

### CORS Configuration
CORS is configured in `app/main.py` with multiple allowed origins including localhost and Vercel deployments.

### Database Migrations
All database schema changes use Alembic migrations in `alembic/versions/`. The system has extensive migration history for church management features.

## Security Considerations

### Data Encryption
- GPT API keys stored encrypted using `app.utils.encryption`
- Church database credentials encrypted in storage
- JWT-based authentication with role-based access control

### Multi-tenancy
- Church-level data isolation enforced at application layer
- Each church's data completely separated
- API endpoints filtered by authenticated user's church_id

### External Database Security
- Church database connections use encrypted credentials
- SQL injection prevention through parameterized queries
- Connection pooling and timeout management

## AI Integration

### OpenAI Service Pattern
AI responses are generated through:
1. Context building with church-specific data
2. System prompt customization per agent
3. External database queries based on user intent
4. Token usage tracking and cost management

### Church Data Integration
The system can query external church databases for:
- Member attendance records
- Financial/donation data
- Event schedules
- Member contact information

### Community Features
Recent additions include comprehensive community management:
- **Music Team Recruitment** - Team formation with instrument needs and scheduling
- **Church Events** - Event announcements with contact field separation
- **Job Posts** - Employment opportunities with detailed requirements
- **Community Sharing** - Resource sharing between church members
- **Community Requests** - Member assistance requests
- **Item Sales** - Church marketplace functionality

## Common Development Tasks

### Adding New API Endpoints
1. Create route handler in `app/api/api_v1/endpoints/`
2. Add Pydantic schemas in `app/schemas/`
3. Include router in `app/api/api_v1/api.py`
4. Update CRUD operations if needed in `app/crud/`
5. For community features, use `/community` prefix pattern

### Database Schema Changes
1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration file
4. Apply: `alembic upgrade head`

**Important Notes:**
- Always use `ForeignKey` and `relationship` for user associations (see `music_team_recruitment.py`)
- Include `created_at` and `updated_at` with explicit timezone support: `DateTime(timezone=True)`
- For timestamp fields, set them explicitly in API endpoints to avoid NULL values
- Use JSON column type for array data (e.g., instruments, skills)

### Adding AI Agent Templates
1. Insert template data in `official_agent_templates` table
2. Update initialization scripts in `app/db/`
3. Test agent creation from template

### Push Notification Features
1. Update `app/models/push_notification.py` for new notification types
2. Modify `app/services/push_notification.py` for delivery logic
3. Add endpoints in `app/api/api_v1/endpoints/push_notifications.py`

### Community Features Development Pattern
When adding new community features, follow this established pattern:
1. **Model**: Create with `author_id` as `ForeignKey("users.id")` and `author` relationship
2. **API Response**: Always include `author_name` field using `recruitment.author.full_name if recruitment.author else "익명"`
3. **Timestamps**: Set `created_at` and `updated_at` explicitly in POST/PUT endpoints
4. **Router**: Register under `/community` prefix in `app/api/api_v1/api.py`
5. **Filtering**: Support standard filters (status, search, pagination)
6. **Data Validation**: Use Pydantic models with required/optional field separation

## Deployment

### Docker Deployment
Use `docker-compose.yml` which includes:
- FastAPI backend service
- Redis for caching and task queue
- Celery worker and beat scheduler

### Database Setup
1. Ensure PostgreSQL/Supabase is configured
2. Run migrations: `alembic upgrade head`
3. Initialize sample data if needed with scripts in project root

### Production Considerations
- Set proper `BACKEND_CORS_ORIGINS` for your domain
- Configure Firebase credentials for push notifications
- Set up proper logging and monitoring
- Use environment-specific configuration files