# VAN Phase: Wager/Bonus System Analysis

## Date: 2025-01-07
## Phase: VAN (Verification & Analysis)
## Complexity Assessment: Level 3

## User Requirements

**Core Request**: Add PHP/Symfony service for wager/bonus system
- Default deposit on first visit (e.g., 1000 credits)
- Bonus doubling (1000 → 2000)
- Wagering requirements (must play through 2000 to unlock)
- Visual progress tracking
- KISS principle - keep it simple for POC

## Current System Analysis

### Existing Architecture
- 6 microservices (Go, Python, Node.js, Angular)
- MongoDB for data storage
- RabbitMQ for async messaging
- Redis for caching
- Distributed tracing with Sentry

### Balance Management Currently
- User Service: Stores balance in MongoDB
- Payment Service: Updates balance after games
- Game Engine: Calculates results only
- Frontend: Displays balance from user service

### Gap Analysis
- No bonus system exists
- No wagering requirement tracking
- No balance segregation (real vs bonus)
- No PHP services in stack

## Proposed Solution

### New Service: Wager/Bonus Service (PHP/Symfony)
**Port**: 8085
**Purpose**: Manage bonuses and wagering requirements

### Core Features (KISS Approach)
1. **Auto Deposit**: First-time users get 1000 bonus credits
2. **Bonus Tracking**: Separate bonus from real balance
3. **Wagering Progress**: Track playthrough requirements
4. **Simple Rules**: 2x wagering requirement (play 2000 to unlock 1000)

### Technical Design

#### Data Model (MongoDB)
```javascript
// user_bonuses collection
{
  user_id: "demo-user-123",
  bonuses: [{
    id: "welcome-bonus",
    amount: 1000,
    wagering_required: 2000,
    wagering_completed: 750,
    status: "active", // active, completed, expired
    created_at: ISODate(),
    expires_at: ISODate()
  }],
  real_balance: 0,
  bonus_balance: 1000,
  total_balance: 1000
}

// wager_history collection
{
  user_id: "demo-user-123",
  game_id: "abc123",
  amount: 10,
  type: "bonus", // bonus or real
  timestamp: ISODate()
}
```

#### API Endpoints
```
POST /api/v1/wager/place
GET /api/v1/wager/status/:userId
POST /api/v1/bonus/claim/welcome
GET /api/v1/bonus/progress/:userId
```

### Integration Flow

1. **New User Flow**:
   ```
   Frontend → API Gateway → User Service (create)
                         → Wager Service (auto-claim welcome bonus)
   ```

2. **Game Play Flow**:
   ```
   Frontend → API Gateway → Wager Service (validate & place wager)
                         → Game Engine (calculate result)
                         → Wager Service (update progress)
                         → Payment Service (update balance if needed)
   ```

### Frontend Updates
- Show total balance (real + bonus)
- Progress bar for wagering requirements
- Separate display of bonus vs real money

### Sentry Integration Points
1. **Performance Monitoring**:
   - Bonus calculation time
   - Wagering validation latency
   - Database query performance

2. **Error Tracking**:
   - Invalid wager attempts
   - Bonus rule violations
   - Concurrent update conflicts

3. **Business Metrics**:
   - Bonus conversion rate
   - Average wagering completion time
   - Bonus abandonment rate

## Implementation Approach

### Phase 1: Basic Service Setup
- Symfony skeleton with API Platform
- MongoDB integration
- Basic endpoints
- Sentry SDK integration

### Phase 2: Core Logic
- Welcome bonus auto-claim
- Wager placement validation
- Progress tracking
- Balance updates

### Phase 3: Integration
- API Gateway routing
- Frontend UI updates
- Service communication
- Distributed tracing

### Phase 4: Polish
- Error scenarios for demo
- Performance bottlenecks
- Business metrics

## Risk Assessment

### Technical Risks
- **Low**: PHP/Symfony is mature and stable
- **Low**: Simple business logic for POC
- **Medium**: Integration complexity with existing services

### Mitigation
- Keep bonus rules simple (just welcome bonus)
- Use existing patterns from other services
- Focus on demonstrating Sentry capabilities

## Success Criteria
1. ✅ New users automatically get 1000 bonus
2. ✅ Wagering progress tracked accurately
3. ✅ Bonus converts to real money after requirements met
4. ✅ Frontend shows clear progress
5. ✅ Sentry tracks all metrics and errors
6. ✅ Distributed traces work end-to-end

## Next Steps
1. Create PHP/Symfony service structure
2. Implement basic bonus logic
3. Integrate with existing services
4. Update frontend UI
5. Add Sentry monitoring
6. Create demo scenarios

## Complexity Justification: Level 3
- New service in new language (PHP)
- Multiple service integrations required
- Frontend updates needed
- Business logic complexity (wagering rules)
- Requires careful state management