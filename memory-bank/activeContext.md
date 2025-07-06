# activeContext.md
Current Phase: VAN
Previous Phase: REFLECT
Task Focus: Add Crash Demonstration Endpoints for Python and Node.js Services
Complexity Level: 3
Start Time: 2025-01-06

## Implementation Complete ✅

### Python Game Engine Service (Tornado)
Added comprehensive debug endpoints:
- `/debug/crash` - Unhandled RuntimeError with rich context
- `/debug/error/{type}` - Various error types (value, type, index, key, zero, custom)
- `/debug/memory-leak` - Memory leak simulation (10MB per request)
- `/debug/infinite-loop` - CPU spike for 5 seconds
- `/debug/async-error` - Async/await error handling demo
- `/debug/threading-error` - Threading errors with multiple threads

**Key Features**:
- Rich runtime context (memory, CPU, threads, Python version)
- Breadcrumbs for tracking user actions
- Custom error types with extra context
- Memory leak tracking with psutil
- Thread-local context in multi-threaded scenarios

### Python Analytics Service (FastAPI)
Added debug endpoints:
- `/api/debug/crash` - Unhandled exception with FastAPI context
- `/api/debug/validation-error` - Pydantic validation errors
- `/api/debug/database-error` - MongoDB aggregation errors
- `/api/debug/timeout` - Async timeout simulation (5s)
- `/api/debug/memory-spike` - Memory spike creation and cleanup
- `/api/debug/slow-query` - Intentionally slow MongoDB query

**Key Features**:
- FastAPI-specific error handling
- Pydantic validation error context
- Database error context with operation details
- Memory profiling with garbage collection
- Performance issue demonstrations
- Custom exception handler with request context

### Node.js Payment Service (Express)
Added debug endpoints:
- `/debug/crash` - Uncaught exception with runtime context
- `/debug/promise-rejection` - Unhandled promise rejection
- `/debug/memory-leak` - Memory leak with circular references (50MB per request)
- `/debug/event-loop-block` - Blocks event loop for 3 seconds
- `/debug/stack-overflow` - Recursive function causing stack overflow
- `/debug/type-error` - Common Node.js type errors
- `/debug/async-error` - Async function errors
- `/debug/database-error` - MongoDB operation errors

**Key Features**:
- Node.js-specific runtime info (heap, RSS, uptime)
- Global memory leak tracking
- Event loop blocking demonstration
- Stack overflow depth tracking
- Express error handler integration

## Summary
- All services now have 100% profiling enabled ✅
- All services have comprehensive crash/error demos ✅
- Rich context added to all errors (breadcrumbs, runtime stats, user info) ✅
- Language-specific error patterns demonstrated ✅
- Consistent with Go service's error handling quality ✅