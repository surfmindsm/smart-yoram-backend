# Smart Yoram Backend Documentation

스마트 교회요람 백엔드 API 서버 문서입니다.

## 📚 문서 목록

### API Documentation
- [Push Notifications API](./push-notifications-api.md) - 푸시 알림 RESTful API 명세
- [Authentication API](./authentication-api.md) - 인증 API (작성 예정)
- [Members API](./members-api.md) - 교인 관리 API (작성 예정)
- [Worship Schedule API](./worship-schedule-api.md) - 예배 일정 API (작성 예정)

### Implementation Guides
- [Push Notifications Implementation](./push-notifications-implementation.md) - 푸시 알림 구현 가이드
- [Database Schema](./database-schema.md) - 데이터베이스 스키마 (작성 예정)
- [Authentication Flow](./authentication-flow.md) - 인증 플로우 (작성 예정)

### Development
- [Setup Guide](./setup-guide.md) - 개발 환경 설정 (작성 예정)
- [Testing Guide](./testing-guide.md) - 테스트 가이드 (작성 예정)
- [Deployment Guide](./deployment-guide.md) - 배포 가이드 (작성 예정)

## 🔗 Quick Links

- [API Swagger Documentation](http://localhost:8000/docs)
- [API ReDoc](http://localhost:8000/redoc)
- [Main Project Documentation](../../docs/README.md)

## 📋 API Overview

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.smartyoram.com/api/v1
```

### Authentication
모든 API는 JWT Bearer Token 인증을 사용합니다.
```
Authorization: Bearer {access_token}
```

### Main API Groups

1. **Authentication** (`/auth`)
   - Login, Logout, Refresh Token
   - User Registration
   - Password Reset

2. **Members** (`/members`)
   - CRUD operations for church members
   - Family relationships
   - Member search

3. **Push Notifications** (`/notifications`)
   - Device registration
   - Send notifications
   - Notification history
   - User preferences

4. **Worship Schedule** (`/worship`)
   - Service schedule management
   - Service categories
   - Attendance integration

5. **Attendance** (`/attendance`)
   - Check-in/out
   - Attendance statistics
   - QR code scanning

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Cache**: Redis (Optional)
- **Task Queue**: Celery (Optional)
- **Push Service**: Firebase Cloud Messaging

### Project Structure
```
app/
├── api/
│   └── api_v1/
│       └── endpoints/    # API endpoints
├── core/                 # Core configurations
├── models/              # Database models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── main.py             # Application entry
```

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Church-level data isolation
- Rate limiting on sensitive endpoints
- Input validation with Pydantic

## 📊 Database

### Main Tables
- `users` - User accounts
- `churches` - Church organizations
- `members` - Church members
- `families` - Family units
- `user_devices` - Push notification devices
- `push_notifications` - Notification history
- `worship_services` - Worship schedules
- `attendances` - Attendance records

## 🚀 Getting Started

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   alembic upgrade head
   ```

3. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📝 Contributing

1. Create feature branch
2. Write tests for new features
3. Update documentation
4. Submit PR with clear description

---

*Last updated: 2024-01-XX*