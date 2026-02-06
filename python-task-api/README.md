# Task Management API

A production-ready FastAPI microservice demonstrating modern cloud-native architecture with:
- **FastAPI** for high-performance async API
- **PostgreSQL** for relational data storage
- **Redis** for caching and session management
- **JWT Authentication** for secure access
- **Docker** containerization
- **Kubernetes/OpenShift** deployment
- **CI/CD** with Azure DevOps and ArgoCD

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
└─────────────┘      │     App      │      └─────────────┘
                     └──────┬───────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Redis    │
                     │   (Cache)   │
                     └─────────────┘
```

## 🚀 Features

### Core Functionality
- ✅ **User Authentication**: JWT-based auth with refresh tokens
- ✅ **Task Management**: Full CRUD operations for tasks
- ✅ **Advanced Filtering**: Search, filter by status/priority, pagination
- ✅ **Caching**: Redis-based caching for performance
- ✅ **Async Operations**: Full async/await for better concurrency

### Production Features
- ✅ **Health Checks**: `/health`, `/ready`, `/live` endpoints
- ✅ **Metrics**: Prometheus metrics at `/metrics`
- ✅ **Auto Documentation**: Swagger UI at `/docs`
- ✅ **Security**: Password hashing, JWT tokens, CORS
- ✅ **Database Migrations**: Alembic for schema management
- ✅ **Structured Logging**: JSON-formatted logs
- ✅ **Type Safety**: Pydantic schemas with validation

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker (optional)

## 🔧 Local Development

### 1. Clone and Setup

```bash
cd python-task-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/taskdb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-this
```

### 3. Start Infrastructure

```bash
# Using Docker Compose (recommended)
docker-compose up -d postgres redis

# Or install locally:
# - PostgreSQL: https://www.postgresql.org/download/
# - Redis: https://redis.io/download
```

### 4. Run Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for Swagger UI
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t task-api:latest .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  task-api:latest
```

## 📚 API Documentation

### Authentication

**Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

### Task Management

**Create Task**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README",
    "priority": "high",
    "status": "todo"
  }'
```

**List Tasks**
```bash
curl http://localhost:8000/api/v1/tasks?page=1&page_size=20 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Task**
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## 📊 Monitoring

### Health Checks

- **Health**: `GET /health` - Basic health check
- **Ready**: `GET /ready` - Database connectivity check
- **Live**: `GET /live` - Liveness probe

### Metrics

Prometheus metrics available at `GET /metrics`:
- HTTP request count
- Request duration histogram
- Custom business metrics

## 🔐 Security Best Practices

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with expiration
- ✅ Non-root Docker user
- ✅ Environment-based secrets
- ✅ CORS configuration
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy)

## 🚢 Kubernetes/OpenShift Deployment

See the `k8s-manifests` repository for:
- Deployment configurations
- Service definitions
- ConfigMaps and Secrets
- Horizontal Pod Autoscaling
- Ingress/Route configurations

## 📈 CI/CD Pipeline

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
- Build and test application
- Build Docker image
- Push to Azure Container Registry
- Update deployment manifests
- Security scanning with Trivy
```

### ArgoCD GitOps

```yaml
# Automatic deployment on manifest changes
- Watches k8s-manifests repository
- Auto-sync enabled
- Rollback capability
- Health assessment
```

## 🏗️ Project Structure

```
python-task-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tasks.py         # Task management endpoints
│   │   └── dependencies.py  # Shared dependencies
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # Auth utilities
│   │   └── cache.py         # Redis caching
│   ├── models/
│   │   └── models.py        # SQLAlchemy models
│   └── schemas/
│       └── schemas.py       # Pydantic schemas
├── tests/
│   ├── test_auth.py
│   └── test_tasks.py
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built as a production-ready portfolio project demonstrating:
- Modern Python development
- Cloud-native architecture
- DevOps best practices
- Microservices patterns

## 🔗 Related Repositories

- [k8s-manifests](../k8s-manifests) - Kubernetes/OpenShift deployment configurations
- Azure DevOps Pipeline - CI/CD automation

---

**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: January 2026
