# Technical Context - Technology Stack & Versions

## Language Versions
- **Go**: 1.18+ (Gateway, User Service, Notification Service)
- **Python**: 3.8+ (Game Engine with Tornado 6.x, Analytics)
- **Node.js**: 14.x+ ES2015+ (Payment Service)
- **Angular**: 13+ (Main Frontend)
- **React**: 17 (Legacy Admin Panel)

## Service-Specific Tech Stack

### API Gateway (Go)
- Framework: Gin or Echo
- Auth: JWT with RS256
- Rate limiting: Built-in or Redis-based
- Sentry SDK: sentry-go

### Game Engine (Python/Tornado)
- Tornado 6.x for async/WebSocket
- NumPy for RNG calculations
- Sentry SDK: sentry-python
- Profiling: CPU intensive operations

### User Service (Go)
- Database: GORM with PostgreSQL
- Cache: go-redis
- Auth: JWT generation/validation
- Sentry SDK: sentry-go

### Payment Service (Node.js)
- Framework: Express or Fastify
- Database: Sequelize/TypeORM
- External APIs: Payment providers
- Sentry SDK: @sentry/node

### Analytics Service (Python)
- Pandas for data processing
- Scheduled jobs with APScheduler
- MongoDB driver: pymongo
- Sentry SDK: sentry-python

### Frontend (Angular)
- Angular 13+
- State: NgRx or Akita
- Build: Webpack with source maps
- Sentry SDK: @sentry/angular

### Admin Panel (React)
- React 17 (legacy)
- State: Redux (outdated patterns)
- Known issues: Memory leaks
- Sentry SDK: @sentry/react

## Infrastructure Components
- Kafka: 2.8+
- Redis: 6.2+
- PostgreSQL: 13+
- MongoDB: 4.4+
- MinIO: Latest
- Docker: For local development

## Development Tools
- Go: golangci-lint
- Python: flake8, black
- Node.js: ESLint, Prettier
- Frontend: Angular CLI, Create React App