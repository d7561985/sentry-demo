# Sentry POC Setup Instructions

## Prerequisites
1. Create a Sentry account at https://sentry.io
2. Create a new project for each service type:
   - JavaScript project for Frontend
   - Node.js project for Payment Service  
   - Python project for Game Engine
   - Go projects for API Gateway and User Service

## Configuration

### 1. Frontend (Angular)
Edit `services/frontend/src/environments/environment.ts` and `environment.prod.ts`:
```typescript
export const environment = {
  production: false, // or true for prod
  sentryDsn: 'YOUR_FRONTEND_SENTRY_DSN',
  apiUrl: 'http://localhost:8080' // or '/api' for prod
};
```

### 2. Backend Services
Set environment variables in `docker-compose.yml` for each service:

```yaml
environment:
  - SENTRY_DSN=YOUR_SERVICE_SPECIFIC_DSN
```

Or create a `.env` file in the root directory:
```
# API Gateway
GATEWAY_SENTRY_DSN=https://xxx@sentry.io/yyy

# User Service  
USER_SERVICE_SENTRY_DSN=https://xxx@sentry.io/yyy

# Game Engine
GAME_ENGINE_SENTRY_DSN=https://xxx@sentry.io/yyy

# Payment Service
PAYMENT_SERVICE_SENTRY_DSN=https://xxx@sentry.io/yyy
```

## Testing the Integration

1. Start all services:
   ```bash
   ./start.sh
   ```

2. Open the frontend at http://localhost:4200

3. Click "SPIN" to trigger a distributed trace across all services

4. Check your Sentry dashboard to see:
   - Distributed traces
   - Error tracking
   - Performance monitoring
   - Custom tags and context

## Features Demonstrated

### Scenario 1: Distributed Tracing
- End-to-end transaction tracing from Frontend → API Gateway → User Service → Game Engine → Payment Service
- W3C trace context propagation
- Service dependency visualization
- Performance bottleneck identification

### Intentional Issues for Demo
1. **User Service**: 500ms slow query simulation
2. **Game Engine**: CPU spike on certain spins
3. **Payment Service**: 10% random failure rate
4. **Frontend**: User context and custom breadcrumbs

## Troubleshooting

If traces are not appearing:
1. Verify all services have valid Sentry DSNs
2. Check service logs for Sentry initialization messages
3. Ensure `tracesSampleRate: 1.0` is set (100% sampling)
4. Verify network connectivity to sentry.io

## Next Steps

After setting up DSNs:
1. Trigger some transactions
2. Explore the Sentry Performance dashboard
3. Check the Distributed Tracing view
4. Review captured errors and their context