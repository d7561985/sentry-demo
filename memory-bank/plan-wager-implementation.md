# PLAN Phase: Wager/Bonus Service Implementation

## Date: 2025-01-07
## Phase: PLAN
## Complexity: Level 3

## Implementation Plan Overview

### Service Architecture
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend  │────▶│ API Gateway  │────▶│ Wager Service│
└─────────────┘     └──────────────┘     └──────┬───────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌──────────────┐
                    │ User Service │     │   MongoDB    │
                    └──────────────┘     └──────────────┘
```

## Phase 1: Service Setup (Day 1)

### 1.1 Create PHP/Symfony Structure
```bash
services/wager-service/
├── Dockerfile
├── docker-compose.override.yml
├── composer.json
├── .env
├── config/
│   ├── packages/
│   ├── routes.yaml
│   └── services.yaml
├── src/
│   ├── Controller/
│   │   ├── WagerController.php
│   │   └── BonusController.php
│   ├── Service/
│   │   ├── WagerService.php
│   │   └── BonusService.php
│   ├── Repository/
│   │   ├── BonusRepository.php
│   │   └── WagerRepository.php
│   └── Entity/
│       ├── Bonus.php
│       └── WagerHistory.php
└── public/
    └── index.php
```

### 1.2 Dependencies (composer.json)
```json
{
    "require": {
        "php": ">=8.1",
        "symfony/framework-bundle": "^6.3",
        "symfony/dotenv": "^6.3",
        "symfony/yaml": "^6.3",
        "doctrine/mongodb-odm-bundle": "^4.6",
        "sentry/sentry-symfony": "^4.14",
        "symfony/monolog-bundle": "^3.10",
        "symfony/http-client": "^6.3"
    }
}
```

### 1.3 Docker Configuration
- Base image: php:8.2-fpm-alpine
- Install required extensions: mongodb, redis
- Configure nginx for Symfony
- Set up health check endpoint

## Phase 2: Core Implementation (Day 1-2)

### 2.1 API Endpoints

#### Bonus Endpoints
```
POST   /api/v1/bonus/welcome/{userId}     # Auto-claim welcome bonus
GET    /api/v1/bonus/active/{userId}      # Get active bonuses
GET    /api/v1/bonus/balance/{userId}     # Get real vs bonus balance
```

#### Wager Endpoints
```
POST   /api/v1/wager/validate             # Validate wager before game
POST   /api/v1/wager/complete             # Record wager result
GET    /api/v1/wager/progress/{userId}    # Get wagering progress
GET    /api/v1/wager/history/{userId}     # Get wager history
```

### 2.2 Data Models

#### Bonus Document (MongoDB)
```php
class Bonus {
    public string $id;
    public string $userId;
    public string $type = 'welcome';
    public float $amount = 1000.0;
    public float $wageringRequired = 2000.0;
    public float $wageringCompleted = 0.0;
    public string $status = 'active'; // active, completed, expired
    public DateTime $createdAt;
    public DateTime $expiresAt;
}
```

#### Wager History Document
```php
class WagerHistory {
    public string $id;
    public string $userId;
    public string $gameId;
    public float $amount;
    public string $type; // 'bonus' or 'real'
    public float $bonusProgress;
    public DateTime $timestamp;
}
```

### 2.3 Business Logic Flow

#### Welcome Bonus Flow
1. User Service creates new user
2. User Service calls Wager Service `/bonus/welcome/{userId}`
3. Wager Service creates bonus record
4. Returns success with bonus details

#### Wager Validation Flow
1. Frontend requests spin
2. API Gateway calls Wager Service `/wager/validate`
3. Wager Service checks:
   - User has sufficient balance (real + bonus)
   - Applies bonus first, then real money
   - Returns validation result
4. If valid, proceed to Game Engine

#### Wager Completion Flow
1. Game Engine calculates result
2. Payment Service calls Wager Service `/wager/complete`
3. Wager Service:
   - Records wager in history
   - Updates wagering progress
   - Converts bonus to real if requirements met
4. Returns updated balance info

## Phase 3: Service Integration (Day 2)

### 3.1 API Gateway Updates
```go
// Add to routes
r.POST("/api/v1/bonus/*", handlers.ProxyToWagerService(cfg))
r.GET("/api/v1/bonus/*", handlers.ProxyToWagerService(cfg))
r.POST("/api/v1/wager/*", handlers.ProxyToWagerService(cfg))
r.GET("/api/v1/wager/*", handlers.ProxyToWagerService(cfg))
```

### 3.2 User Service Integration
```go
// In CreateUser handler, after user creation:
resp, err := http.Post(
    fmt.Sprintf("http://wager-service:8085/api/v1/bonus/welcome/%s", userId),
    "application/json",
    nil,
)
```

### 3.3 Payment Service Integration
```javascript
// After game result processing:
const wagerResult = await axios.post('http://wager-service:8085/api/v1/wager/complete', {
    userId,
    gameId,
    amount: bet,
    result: gameResult
});
```

## Phase 4: Frontend Updates (Day 3)

### 4.1 UI Components
- Bonus balance display (separate from real balance)
- Wagering progress bar
- Bonus information tooltip
- Combined balance display

### 4.2 State Management
```typescript
interface UserBalance {
    realBalance: number;
    bonusBalance: number;
    totalBalance: number;
    activeBonus?: {
        type: string;
        wageringRequired: number;
        wageringCompleted: number;
        progressPercentage: number;
    };
}
```

## Phase 5: Sentry Integration (Day 3)

### 5.1 Performance Monitoring
- Transaction traces for all endpoints
- Database query performance
- Service-to-service latency

### 5.2 Error Scenarios
```php
// Insufficient balance
if ($totalBalance < $wagerAmount) {
    throw new InsufficientBalanceException(
        sprintf('Balance: %.2f, Required: %.2f', $totalBalance, $wagerAmount)
    );
}

// Concurrent wager attempt
if ($this->isWagerInProgress($userId)) {
    throw new ConcurrentWagerException('Wager already in progress');
}

// Expired bonus usage
if ($bonus->isExpired()) {
    throw new ExpiredBonusException('Bonus expired on ' . $bonus->expiresAt);
}
```

### 5.3 Business Metrics
- Bonus claim rate
- Wagering completion rate
- Average time to complete wagering
- Bonus conversion rate

## Phase 6: Testing & Demo Scenarios (Day 4)

### 6.1 Happy Path
1. New user → Auto-claim bonus → Play games → Complete wagering → Convert to real

### 6.2 Error Scenarios
1. Insufficient balance attempts
2. Expired bonus usage
3. Concurrent wager attempts
4. Service communication failures

### 6.3 Performance Scenarios
1. N+1 query in wager history
2. Slow bonus calculation
3. Database connection pool exhaustion

## Implementation Sequence

### Day 1: Foundation
- [ ] Create Symfony project structure
- [ ] Set up Docker configuration
- [ ] Implement basic controllers
- [ ] Configure MongoDB connection

### Day 2: Core Logic
- [ ] Implement bonus service
- [ ] Implement wager validation
- [ ] Add progress tracking
- [ ] Create API endpoints

### Day 3: Integration
- [ ] Update API Gateway
- [ ] Integrate with User Service
- [ ] Integrate with Payment Service
- [ ] Add Sentry monitoring

### Day 4: Frontend & Polish
- [ ] Update frontend components
- [ ] Add progress visualization
- [ ] Test error scenarios
- [ ] Create demo scripts

## Risk Mitigation

### Technical Risks
1. **PHP/Symfony setup complexity**
   - Mitigation: Use symfony/skeleton for quick setup
   
2. **Service coordination**
   - Mitigation: Clear API contracts, proper error handling

3. **Balance consistency**
   - Mitigation: Single source of truth (Wager Service)

### Business Risks
1. **Complex bonus rules**
   - Mitigation: Single bonus type, fixed multiplier

2. **Edge cases**
   - Mitigation: Document assumptions, handle gracefully

## Success Metrics
- [ ] Welcome bonus auto-claimed for new users
- [ ] Wagering progress tracked accurately
- [ ] Bonus converts to real after 2x wagering
- [ ] All services integrated with distributed tracing
- [ ] Error scenarios demonstrate Sentry value
- [ ] Frontend shows clear bonus information