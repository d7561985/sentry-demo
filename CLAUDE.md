# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a POC (Proof of Concept) for demonstrating Sentry monitoring capabilities in an iGaming platform context. The project aims to showcase how Sentry can improve reliability, performance, and user experience in a critical gaming system.

## POC Goals & Focus

**PRIMARY GOAL**: Create minimal, working code that effectively demonstrates Sentry's value for iGaming platforms.

### Key Demonstration Points:
- **MTTR Reduction**: Show how Sentry reduces issue resolution time from 4-6 hours to 30-60 minutes
- **Error Rate Improvement**: Demonstrate tracking and reducing errors from 2.5% to <0.5%
- **Performance Gains**: Show P95 latency improvements from 800ms to 200ms
- **Alert Noise Reduction**: From 200 to 10 meaningful alerts per day

### Development Approach:
- **Minimal Viable Code** - Just enough to demonstrate each Sentry feature
- **Real Scenarios** - Include actual bugs, performance issues, and errors
- **Quick Setup** - Services should be easy to run locally
- **Clear Demos** - Each issue should be easily reproducible

## Technology Stack

### Language Versions & Frameworks:
- **Go**: 1.18+
- **Python**: 3.8+ with Tornado 6.x
- **Node.js**: 14.x+ (ES2015+)
- **Angular**: 13+
- **React**: 17

## Architecture

The system consists of 8 microservices with different technology stacks:

1. **API Gateway (Go)** - Entry point, rate limiting, authentication/JWT
2. **Game Engine Service (Python/Tornado)** - Core game logic, WebSocket connections
3. **User Service (Go)** - User profiles, sessions, KYC
4. **Payment Service (Node.js)** - Payment integrations, deposits/withdrawals
5. **Analytics Service (Python)** - Real-time metrics, fraud detection
6. **Notification Service (Go)** - Email/SMS/Push, message queue consumer
7. **Web Frontend (Angular)** - Main gaming interface
8. **Admin Panel (React)** - Legacy code with technical debt

### Infrastructure Components
- **Message Queue**: RabbitMQ for async analytics data collection
- **Cache**: Redis for sessions and hot data
- **Database**: MongoDB for all data storage (simplified for POC)
- **Storage**: MinIO for game assets (future enhancement)

## Development Guidelines

### POC Implementation Priorities:
1. Start with minimal service scaffolding
2. Add just enough endpoints to demonstrate distributed tracing
3. Include intentional issues (memory leaks, slow queries, crashes)
4. Focus on Sentry integration over feature completeness
5. Use mock data and simplified business logic

### Service Structure
Each microservice should follow its language's conventions:
- Go services: Use standard project layout with cmd/, internal/, pkg/
- Python services: Follow PEP8, use requirements.txt or poetry
- Node.js services: Use npm/yarn, follow Express/Fastify patterns
- Frontend: Component-based architecture with proper state management

### Sentry Integration Points
1. SDK initialization in all services with proper context
2. Custom instrumentation for business metrics (RTP, active sessions, bet volumes)
3. Source maps for frontend builds
4. Profiling for CPU/Memory intensive operations
5. Session replay for frontend
6. Cron monitoring for scheduled jobs
7. Feature flags integration

### Key Monitoring Scenarios
- Distributed tracing across services
- Performance issues (slow queries, N+1 problems, blocking operations)
- Error tracking (4xx, 5xx, exceptions, panics)
- Memory profiling (especially React admin panel)
- Custom business metrics
- Release tracking with regression detection
- User context binding to errors

## Common Commands

Since this is a new project, specific build commands will be added as services are implemented. Expected commands per service type:

### Go Services
```bash
go mod init <service-name>
go build ./cmd/<service-name>
go test ./...
golangci-lint run
```

### Python Services
```bash
pip install -r requirements.txt
python -m pytest
flake8 .
black .
```

### Node.js Services
```bash
npm install
npm run dev
npm test
npm run lint
```

### Frontend (Angular/React)
```bash
npm install
npm start
npm run build
npm test
npm run lint
```

## Architecture Principles

1. **KISS (Keep It Simple, Stupid)** - Focus on demonstrating Sentry capabilities, not over-engineering
2. **Microservices Communication** - Use REST for synchronous, Kafka for async
3. **Error Handling** - Proper error context and user information for Sentry
4. **Performance** - Include intentional bottlenecks for Sentry demonstration
5. **Security** - JWT for auth, no hardcoded secrets, use environment variables

## Important Notes

- This is a POC focused on Sentry integration demonstration
- Include realistic scenarios: memory leaks, slow queries, error conditions
- Each service should have clear boundaries and responsibilities
- Use context7 MCP for analyzing latest library updates when needed
- Avoid significant architecture changes without approval

## Development Process - Memory Bank System

This project uses an adaptive memory-based assistant system with specialized modes for different development phases. Each mode has specific rules and processes defined in isolation_rules/visual-maps/.

### Available Modes:
- **VAN**: Initial exploration and requirements understanding
- **PLAN**: Planning and architecture design
- **CREATIVE**: Creative problem solving and design
- **IMPLEMENT**: Code implementation
- **QA**: Quality assurance and testing

### Memory Bank Files:
- **tasks.md**: Single source of truth for all task tracking
- **projectbrief.md**: Foundation document with project requirements
- **activeContext.md**: Current focus and active work
- **progress.md**: Implementation status tracking

### Mode Usage:
When starting work, declare the mode (e.g., "VAN", "PLAN", etc.) to activate the appropriate process. The system will:
1. Respond with "OK [MODE]"
2. Check Memory Bank status
3. Load appropriate rules from isolation_rules/visual-maps/
4. Execute the process while maintaining context
5. Update Memory Bank continuously

### Verification Commitment:
- Follow the appropriate visual process map
- Run all verification checkpoints
- Maintain tasks.md as the single source of truth