# Active Context - Current Focus

## Current Mode: PLAN - Scenario 4

## Previous Work Completed
- Scenario 1: Distributed Tracing ✅ ARCHIVED
- Frontend Enhancement: Animated slot machine ✅
- Scenario 2: Error Tracking Suite ✅ ARCHIVED
- Source Maps Configuration ✅
- Session Replay Feature ✅
- Scenario 3: Performance Monitoring ✅ ARCHIVED

## Active Focus
**Scenario 4: Business Metrics Monitoring**

## Scenario 4 Implementation Plan

### Overview
Demonstrate Sentry's custom metrics capabilities for tracking critical business KPIs in an iGaming platform. Show how to monitor RTP (Return to Player), financial metrics, and player activity in real-time.

### Key Business Metrics to Track

1. **Game Metrics (Game Engine)**
   - RTP (Return to Player) percentage
   - Win/loss ratios per session
   - Bet volumes and patterns
   - Game round durations

2. **Financial Metrics (Payment Service)**
   - Deposit/withdrawal volumes
   - Payment success/failure rates
   - Revenue tracking
   - Average transaction size

3. **Player Activity (Analytics Service)**
   - Active sessions count
   - Player retention rates
   - Session duration metrics
   - Geographic distribution

4. **System Health Metrics**
   - API response times by endpoint
   - Queue processing rates
   - Cache hit/miss ratios
   - Service availability

### Implementation Details

#### 1. Game Engine Service Enhancements
```python
# Custom metrics for each spin
sentry_sdk.set_measurement("bet_amount", bet_amount, "currency")
sentry_sdk.set_measurement("payout", payout, "currency")
sentry_sdk.set_measurement("rtp_current", current_rtp, "percentage")
sentry_sdk.set_measurement("spin_duration", duration, "millisecond")
```

#### 2. Payment Service Metrics
```javascript
// Track financial metrics
Sentry.setMeasurement("transaction_amount", amount, "currency");
Sentry.setMeasurement("payment_duration", duration, "millisecond");
Sentry.setTag("payment_method", method);
Sentry.setTag("transaction_type", type);
```

#### 3. Analytics Service Aggregation
```python
# Aggregate and send business metrics
metrics = {
    "active_sessions": count_active_sessions(),
    "hourly_rtp": calculate_hourly_rtp(),
    "total_revenue": get_revenue_metrics(),
    "player_count": get_unique_players()
}
```

#### 4. Frontend Dashboard
- Real-time RTP display
- Active sessions counter
- Revenue metrics visualization
- Performance indicators

### Demo Scenarios

1. **RTP Anomaly Detection**
   - Button to temporarily skew RTP (e.g., 150% or 50%)
   - Show alert triggering in Sentry
   - Demonstrate metric history and trends

2. **Revenue Monitoring**
   - Simulate revenue spike/drop
   - Show financial dashboard
   - Alert on unusual patterns

3. **Player Activity Surge**
   - Simulate sudden increase in active sessions
   - Show system behavior under load
   - Monitor resource usage

### Sentry Configuration

1. **Custom Units**
   - currency: For monetary values
   - percentage: For RTP and rates
   - count: For sessions and players
   - millisecond: For durations

2. **Dashboards**
   - Business KPIs Dashboard
   - Financial Overview
   - Player Activity Monitor
   - System Health Metrics

3. **Alerts**
   - RTP deviation > 5% from baseline
   - Revenue drop > 20% hour-over-hour
   - Active sessions > 1000
   - Payment failure rate > 10%

### Success Criteria
- All services sending custom metrics
- Business dashboard showing real-time KPIs
- Alerts configured and triggering correctly
- Demo scenarios working smoothly
- Clear value demonstration for iGaming platform monitoring

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
1. **Scenario 3: Performance Monitoring** 🔍 CURRENT
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

## Scenario 3 Requirements Analysis
### Performance Issues to Demonstrate:
1. **User Service - N+1 Query Problem**
   - Fetch user, then fetch each game history separately
   - Show in Sentry performance view
   - Endpoint: `/api/v1/user/:userId/history`
   
2. **Game Engine - CPU Spike**
   - Inefficient RNG calculation (prime number generation)
   - Show CPU profiling in Sentry
   - Add query param: `?cpu_intensive=true`
   
3. **Analytics Service - Slow Aggregation**
   - Create new Python service
   - Unoptimized MongoDB aggregation pipeline
   - Missing indexes on game_sessions collection
   - Endpoint: `/api/v1/analytics/daily-stats`
   
4. **Payment Service - External API Latency**
   - Already implemented (2-5s delay) ✅
   - Need to highlight in performance dashboard

### Detailed Implementation Plan
1. **User Service Enhancement**
   - Add game history model
   - Create `/history` endpoint with intentional N+1
   - Each game fetch = separate DB query
   
2. **Game Engine CPU Spike**
   - Add inefficient prime calculation for RNG seed
   - Toggle via query parameter
   - Should spike CPU for ~1-2 seconds
   
3. **Analytics Service Creation**
   - Python/FastAPI service
   - MongoDB aggregation for daily stats
   - Intentionally missing compound index
   - Full collection scan on large dataset
   
4. **Frontend Debug Panel Update**
   - Add "Performance Tests" section
   - Buttons for each scenario
   - Show performance metrics inline

### Safety Requirements
**CRITICAL**: Performance features MUST NOT break existing functionality
- All performance issues behind feature flags/params
- Default behavior remains fast
- Only trigger performance issues on demand
- Maintain distributed tracing integrity

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