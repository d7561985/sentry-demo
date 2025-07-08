# Creative: Wager Service Architecture Design

## Date: 2025-01-07
## Phase: CREATIVE
## Challenge: PHP/Symfony Service Architecture

## Problem Statement
Design the architecture for a PHP/Symfony microservice that handles bonus and wagering functionality while:
- Maintaining simplicity (KISS principle)
- Demonstrating Sentry monitoring capabilities
- Integrating with existing microservices
- Handling concurrent operations safely

## Architecture Options

### Option 1: Traditional MVC with Repository Pattern
```
┌─────────────┐
│ Controller  │ → HTTP endpoints
├─────────────┤
│  Service    │ → Business logic
├─────────────┤
│ Repository  │ → Data access
├─────────────┤
│   Entity    │ → Domain models
└─────────────┘
```

**Pros:**
- Standard Symfony pattern, well documented
- Clear separation of concerns
- Easy to test each layer
- Symfony developers will understand immediately

**Cons:**
- More boilerplate code
- Might be overkill for POC
- Additional abstraction layers

**Complexity:** Medium
**Time:** 2 days

### Option 2: Simple MVC with Service Layer
```
┌─────────────┐
│ Controller  │ → Thin HTTP layer
├─────────────┤
│  Service    │ → All business logic + DB
└─────────────┘
```

**Pros:**
- Simpler structure
- Faster to implement
- Less code to maintain
- Still follows Symfony conventions

**Cons:**
- Services become larger
- Less separation of concerns
- Harder to unit test

**Complexity:** Low
**Time:** 1 day

### Option 3: Event-Driven Architecture
```
┌─────────────┐
│ Controller  │ → Dispatch events
├─────────────┤
│   Events    │ → Domain events
├─────────────┤
│  Handlers   │ → Process events
├─────────────┤
│ Projections │ → Read models
└─────────────┘
```

**Pros:**
- Excellent for Sentry event tracking
- Natural audit trail
- Decoupled components
- Easy to add new features

**Cons:**
- Complex for POC
- Longer implementation time
- Team needs event sourcing knowledge

**Complexity:** High
**Time:** 4 days

## Decision: Option 2 - Simple MVC with Service Layer

### Rationale
1. **KISS Principle**: Simplest approach that meets requirements
2. **POC Focus**: Demonstrates functionality without over-engineering
3. **Time Efficiency**: Can implement in 1 day vs 2-4 days
4. **Sentry Integration**: Service layer provides clear transaction boundaries
5. **Team Familiarity**: Standard Symfony pattern everyone knows

### Implementation Structure
```
services/wager-service/
├── src/
│   ├── Controller/
│   │   ├── BonusController.php    # Bonus endpoints
│   │   └── WagerController.php    # Wager endpoints
│   ├── Service/
│   │   ├── BonusService.php       # Bonus logic + DB
│   │   ├── WagerService.php       # Wager logic + DB
│   │   └── IntegrationService.php # External service calls
│   ├── Document/                   # MongoDB documents
│   │   ├── Bonus.php
│   │   └── WagerHistory.php
│   └── Exception/                  # Custom exceptions
│       ├── InsufficientBalanceException.php
│       ├── BonusExpiredException.php
│       └── ConcurrentWagerException.php
```

### Service Responsibilities

#### BonusService
- Create welcome bonus
- Check active bonuses
- Calculate bonus balance
- Convert bonus to real money

#### WagerService
- Validate wager amount
- Record wager history
- Update wagering progress
- Check completion status

#### IntegrationService
- Call User Service
- Call Payment Service
- Handle distributed tracing
- Manage retries

### Sentry Integration Points
```php
class WagerService {
    public function validateWager($userId, $amount) {
        $span = SentrySdk::getCurrentHub()->getSpan();
        $span->setOp('wager.validate');
        $span->setDescription('Validate wager amount');
        
        // Add business context
        $span->setData('user_id', $userId);
        $span->setData('wager_amount', $amount);
        
        // Business logic with performance tracking
        $balance = $this->calculateTotalBalance($userId);
        
        if ($balance < $amount) {
            throw new InsufficientBalanceException();
        }
    }
}
```

### Error Handling Strategy
- Use custom exceptions for business errors
- Let Symfony handle HTTP responses
- Sentry captures all exceptions automatically
- Add context in service methods

### Performance Considerations
- Index MongoDB on userId for fast lookups
- Cache active bonus in Redis (future)
- Batch wager history inserts
- Use MongoDB aggregation for progress calculation