# Sentry Demo Scenarios - Detailed Plan

## Scenario 1: Distributed Tracing Demo
**Goal**: Show complete request flow through all services

### Setup
```
User Story: Player spins slot machine
Flow: Frontend → Gateway → User → Game → Payment → Response
```

### Implementation
1. Frontend: "Spin" button with trace initiation
2. Gateway: Add user context, auth check
3. User Service: Check balance (with intentional slow query)
4. Game Engine: Calculate result (CPU spike)
5. Payment Service: Update balance (random failures)

### What to Show in Sentry
- Complete trace visualization
- Service dependencies
- Performance bottlenecks
- Error propagation

---

## Scenario 2: Error Tracking Suite
**Goal**: Demonstrate different error types and contexts

### Errors to Implement
1. **Frontend JS Error**
   - Unhandled promise rejection
   - React error boundary catch

2. **Gateway Panic** (Go)
   ```go
   // Triggered by specific user ID
   if userID == "panic-test" {
       panic("Demo panic for Sentry")
   }
   ```

3. **Payment Service 500**
   ```js
   // 10% random failure
   if (Math.random() < 0.1) {
       throw new Error("Payment provider timeout")
   }
   ```

4. **User Service 401**
   - Invalid token handling

### What to Show in Sentry
- Error grouping
- Stack traces
- User context
- Error frequency

---

## Scenario 3: Performance Monitoring
**Goal**: Identify and fix performance issues

### Performance Issues
1. **N+1 Query** (User Service)
   ```go
   // Bad: Load games for each user separately
   for _, user := range users {
       games := loadUserGames(user.ID)
   }
   ```

2. **Missing Index** (MongoDB)
   ```js
   // Slow query without index
   db.games.find({ userId: id, timestamp: { $gte: date } })
   ```

3. **Memory Leak** (React Admin)
   ```jsx
   // Never cleaned up interval
   componentDidMount() {
       setInterval(() => this.loadData(), 1000)
   }
   ```

4. **CPU Spike** (Game Engine)
   ```python
   # Inefficient RNG calculation
   for i in range(1000000):
       result = complex_calculation()
   ```

### What to Show in Sentry
- Transaction details
- Database query performance
- Memory profiling
- CPU profiling

---

## Scenario 4: Custom Business Metrics
**Goal**: Track gaming-specific KPIs

### Metrics to Implement
1. **RTP Tracking**
   ```python
   sentry_sdk.set_measurement("rtp", calculated_rtp)
   sentry_sdk.set_tag("game_type", "slot")
   ```

2. **Active Sessions**
   ```go
   sentry.CaptureMetric("active_sessions", activeCount)
   ```

3. **Payment Success Rate**
   ```js
   Sentry.metrics.gauge('payment.success_rate', successRate)
   ```

### What to Show in Sentry
- Custom dashboards
- Metric trends
- Alerting on thresholds

---

## Scenario 5: Release Tracking
**Goal**: Show regression detection

### Implementation
1. **Version 1.0**: Deploy working version
2. **Version 1.1**: Introduce bug
   ```js
   // Regression: Wrong calculation
   const payout = bet * 0.5 // Should be bet * multiplier
   ```
3. **Version 1.2**: Fix bug

### What to Show in Sentry
- Error spike after release
- Release comparison
- Deployment tracking
- Quick rollback decision

---

## Scenario 6: Alert Optimization
**Goal**: Reduce noise, focus on critical issues

### Alerts to Configure
1. **Critical**: Payment failures > 5%
2. **High**: P95 latency > 500ms
3. **Medium**: Error rate > 1%
4. **Low**: New error type detected

### What to Show in Sentry
- Alert rules configuration
- Notification routing
- Alert history
- Noise reduction

---

## Testing Plan for Each Scenario

### Scenario Test Template
```yaml
scenario: [Name]
setup:
  - Start all services
  - Configure Sentry
  - Enable specific feature flags
  
steps:
  1. Execute trigger action
  2. Verify issue appears in Sentry
  3. Show relevant dashboards
  4. Demonstrate fix
  
validation:
  - Issue correctly captured
  - Context properly attached
  - Metrics recorded
  - Alerts triggered (if applicable)
```

## Implementation Priority
1. Distributed Tracing (foundation)
2. Error Tracking (immediate value)
3. Performance Monitoring (common pain point)
4. Custom Metrics (business value)
5. Release Tracking (DevOps integration)
6. Alert Management (operational efficiency)