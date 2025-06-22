# Active Context - Current Focus

## Current Mode: ARCHIVE - Ready for Next Task

## Previous Work Completed
- Scenario 1: Distributed Tracing ✅ ARCHIVED
- Frontend Enhancement: Animated slot machine ✅
- Scenario 2: Error Tracking Suite ✅ ARCHIVED

## Active Focus
Awaiting next task selection

## Scenario 2 Requirements Analysis
### Frontend JS Errors Needed:
1. **Unhandled Promise Rejection**
   - Add async operation that can fail
   - Show in browser console and Sentry
   
2. **Angular Error Boundary**
   - Implement ErrorHandler
   - Catch component errors

### Backend Errors Already Available:
1. **Gateway Panic** ✅
   - Endpoint: `/api/v1/debug/panic/:userId`
   - Already implemented
   
2. **Payment Service 500** ✅
   - 10% random failure rate
   - Already implemented

### Additional Errors to Add:
1. **User Service 401**
   - Invalid token handling
   - Need to add auth validation

## Implementation Plan for Scenario 2
1. Add unhandled promise rejection in frontend
2. Implement Angular ErrorHandler
3. Add invalid token scenario
4. Create demo script to trigger all errors
5. Document error contexts and grouping

## Key Decisions Made (Revised)
1. **Подход**: Сценарно-ориентированная разработка
2. **БД**: Только MongoDB + Redis (упрощение)
3. **Бизнес-логика**: Минимальная слот-игра
4. **Фокус**: 6 ключевых сценариев Sentry
5. **Связность**: Все сервисы в одном trace flow

## Scenario-Driven Development
Вместо разработки по сервисам, работаем по сценариям:
1. **Distributed Tracing** ✅ - основа всего
2. **Error Tracking** 🔄 - разные типы ошибок (CURRENT)
3. **Performance** - N+1, slow queries, memory leaks
4. **Custom Metrics** - RTP, sessions, success rate
5. **Release Tracking** - regression demo
6. **Alerts** - noise reduction

## Implementation Strategy
```
Scenario → Required Services → Minimal Code → Test → Demo
```

## Available Next Scenarios
1. **Scenario 3: Performance Monitoring**
   - N+1 queries, slow operations
   - Memory profiling
   - CPU usage tracking
   
2. **Scenario 4: Custom Business Metrics**
   - RTP tracking
   - Active sessions
   - Success rates
   
3. **Scenario 5: Release Tracking**
   - Version comparison
   - Regression detection
   
4. **Scenario 6: Alert Optimization**
   - Reduce noise
   - Focus on critical issues

## Recommended Next Step
Return to VAN mode to plan next scenario or proceed with git commit if requested.

## Safety Requirements
**CRITICAL**: Scenario 2 implementation MUST NOT break Scenario 1 (Distributed Tracing)
- All new error features must be additive only
- No modifications to existing spin functionality
- Error triggers must be separate from main game flow
- Test distributed tracing after each change

## Detailed Implementation Tasks

### Frontend Tasks
1. **Add Promise Rejection Error**
   - Create new method in game.service.ts that fails randomly
   - Don't catch the error to demonstrate unhandled rejection
   - Sentry will auto-capture with full context

2. **Implement Angular ErrorHandler**
   - Create custom error handler class
   - Register in app.module.ts providers
   - Add method that throws error in component

3. **Debug Panel UI**
   - Add collapsible debug panel to slot machine
   - Buttons: "Trigger Promise Error", "Trigger Component Error", "Trigger Gateway Panic", "Trigger Auth Error"
   - Show current error state

### Backend Tasks  
1. **User Service 401 Implementation**
   - Add middleware to check Authorization header
   - Return 401 if token is "invalid-token"
   - Include proper error context for Sentry

### Testing Flow
1. Start all services
2. Open frontend
3. Use debug panel to trigger each error
4. Verify in Sentry dashboard:
   - Error grouping by type
   - Stack traces
   - User context
   - Distributed trace context