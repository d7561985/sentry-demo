# Task: Add Crash Demonstration Endpoints for Python and Node.js Services

## Description
Implement comprehensive crash and error demonstration endpoints for Python and Node.js services, similar to the Go API Gateway's `/debug/panic` endpoint. This will showcase Sentry's error tracking capabilities across different language stacks with rich context and proper error handling.

## Complexity
Level: 3
Type: Feature

## Technology Stack
- Python Services: Tornado 6.x (Game Engine), FastAPI (Analytics)
- Node.js Service: Express 4.x (Payment)
- Monitoring: Sentry SDK (Python 2.18.0, Node.js 8.0.0)
- All services have profiling enabled at 100%

## Requirements
- Add debug endpoints to trigger various error types
- Include rich context (memory, CPU, request details)
- Demonstrate proper error handling and recovery
- Show different error severities and fingerprinting
- Add breadcrumbs for tracking user actions
- Maintain consistency with Go service implementation

## Status
- [x] Initialization complete (VAN phase)
- [x] Current configuration analyzed
- [ ] Planning complete
- [ ] Implementation
- [ ] Testing
- [ ] Reflection
- [ ] Archiving

## Investigation Results
- **Python Services**: Have profiling at 100%, missing crash demo endpoints
- **Node.js Service**: Has profiling at 100%, limited error demonstrations
- **Go Service Reference**: Has comprehensive `/debug/panic` endpoint with rich context
- **All Services**: Already have Sentry SDK properly configured

## Implementation Plan

### Phase 1: Python Game Engine Service
1. Add debug endpoints
   - [ ] `/debug/crash` - Unhandled exception
   - [ ] `/debug/error/:type` - Different error types
   - [ ] `/debug/memory-leak` - Memory exhaustion
   - [ ] `/debug/infinite-loop` - CPU spike
   - [ ] `/debug/async-error` - Async/await errors

### Phase 2: Python Analytics Service
1. Add debug endpoints
   - [ ] `/api/debug/crash` - Unhandled exception
   - [ ] `/api/debug/validation-error` - Pydantic validation
   - [ ] `/api/debug/database-error` - MongoDB errors
   - [ ] `/api/debug/timeout` - Request timeout

### Phase 3: Node.js Payment Service
1. Add debug endpoints
   - [ ] `/debug/crash` - Uncaught exception
   - [ ] `/debug/promise-rejection` - Unhandled rejection
   - [ ] `/debug/memory-leak` - Memory growth
   - [ ] `/debug/event-loop-block` - Blocking operation
   - [ ] `/debug/stack-overflow` - Recursive error

### Phase 4: Enhanced Error Context
1. Add rich context to all errors
   - [ ] Runtime stats (memory, CPU)
   - [ ] Request details
   - [ ] User context
   - [ ] Breadcrumbs for actions
   - [ ] Custom fingerprinting

## Design Decisions
- Follow Go service pattern for consistency
- Use language-specific error types
- Include runtime diagnostics
- Add controlled crash scenarios
- Implement proper error recovery

---

# Previous Completed Tasks

## Sentry Independent Traces Implementation - COMPLETED ✅
- **Date**: 2025-01-06
- **Archive**: /docs/archive/tasks/sentry-independent-traces-20250106.md
- **Summary**: Implemented independent transaction traces using startNewTrace()

## Angular 13 → 20 Migration - COMPLETED ✅
- **Date**: 2025-01-05
- **Summary**: Sequential migration through 7 major versions with signals implementation