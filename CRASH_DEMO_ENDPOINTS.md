# Crash Demonstration Endpoints

This document describes the crash and error demonstration endpoints available across all services in the Sentry POC.

## Frontend Debug Panel

The slot machine frontend now includes a comprehensive debug panel with buttons to trigger all crash scenarios. Click "🐛 Show Debug Panel" to access:

### Service Crashes
- **Game Engine Crash** - Triggers unhandled RuntimeError in Python/Tornado
- **Analytics Crash** - Triggers unhandled RuntimeError in Python/FastAPI  
- **Payment Crash** - Triggers unhandled Error in Node.js/Express

### Memory & Threading
- **Game Engine Memory Leak** - Creates 10MB memory leak per request
- **Payment Memory Leak** - Creates 50MB memory leak with circular references
- **Threading Error** - Demonstrates threading errors in Python

### Service-Specific Errors
- **Validation Error** - Pydantic validation errors in analytics
- **Payment Promise Rejection** - Unhandled promise rejection in Node.js
- **Event Loop Block** - Blocks Node.js event loop for 3 seconds

## Direct API Endpoints

All endpoints are accessible through the API Gateway at `http://localhost:8080/api/v1/`

### Python Game Engine Service (Tornado)
- `GET /api/v1/game-engine/debug/crash` - Unhandled exception
- `GET /api/v1/game-engine/debug/error/{type}` - Specific error types:
  - `value` - ValueError
  - `type` - TypeError  
  - `index` - IndexError
  - `key` - KeyError
  - `zero` - ZeroDivisionError
  - `custom` - Custom GameEngineError
- `GET /api/v1/game-engine/debug/memory-leak` - Memory leak (10MB)
- `GET /api/v1/game-engine/debug/infinite-loop` - CPU spike (5 seconds)
- `GET /api/v1/game-engine/debug/async-error` - Async/await errors
- `GET /api/v1/game-engine/debug/threading-error` - Threading errors

### Python Analytics Service (FastAPI)
- `GET /api/v1/analytics/debug/crash` - Unhandled exception
- `GET /api/v1/analytics/debug/validation-error` - Pydantic validation
- `GET /api/v1/analytics/debug/database-error` - MongoDB errors
- `GET /api/v1/analytics/debug/timeout` - Async timeout (5s)
- `GET /api/v1/analytics/debug/memory-spike` - Memory spike demo
- `GET /api/v1/analytics/debug/slow-query` - Slow database query

### Node.js Payment Service (Express)
- `GET /api/v1/payment/debug/crash` - Uncaught exception
- `GET /api/v1/payment/debug/promise-rejection` - Unhandled promise
- `GET /api/v1/payment/debug/memory-leak` - Memory leak (50MB)
- `GET /api/v1/payment/debug/event-loop-block` - Event loop blocking
- `GET /api/v1/payment/debug/stack-overflow` - Stack overflow
- `GET /api/v1/payment/debug/type-error` - TypeError
- `GET /api/v1/payment/debug/async-error` - Async function error
- `GET /api/v1/payment/debug/database-error` - MongoDB operation error

### Go API Gateway
- `GET /api/v1/debug/panic/panic-test` - Panic with rich context

## Testing Script

Use the provided test script to quickly test all endpoints:

```bash
./test-crash-endpoints.sh
```

## What to Look for in Sentry

1. **Error Details**:
   - Full stack traces (even for Go with custom error package)
   - Breadcrumbs showing user actions before crash
   - Runtime context (memory, CPU, threads)
   - User context and request details

2. **Performance Monitoring**:
   - Distributed traces across services
   - Memory profiling data
   - CPU spike detection
   - Event loop blocking in Node.js

3. **Business Impact**:
   - Crash-free rate metrics
   - Session tracking
   - Release health
   - Error grouping and fingerprinting

## Key Features Demonstrated

- **100% Profiling**: All services have profiling enabled at 100%
- **Rich Context**: Every error includes comprehensive debugging information
- **Language-Specific**: Demonstrates unique error patterns for each stack
- **Distributed Tracing**: Errors maintain trace context across services
- **Memory Profiling**: Shows memory leaks and spikes
- **Threading Issues**: Python threading and Node.js event loop problems