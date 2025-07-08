# Creative: Wager Service Data Model Design

## Date: 2025-01-07
## Phase: CREATIVE
## Challenge: MongoDB Schema Design for Bonus/Wager System

## Problem Statement
Design a MongoDB schema that:
- Tracks bonuses and wagering progress efficiently
- Maintains audit trail for compliance
- Supports concurrent operations
- Enables fast queries for real-time progress
- Demonstrates Sentry performance monitoring

## Data Model Options

### Option 1: Normalized Collections
```javascript
// bonuses collection
{
  _id: ObjectId,
  user_id: "user-123",
  type: "welcome",
  amount: 1000,
  status: "active",
  created_at: ISODate()
}

// wager_progress collection
{
  _id: ObjectId,
  bonus_id: ObjectId,
  wagering_required: 2000,
  wagering_completed: 500,
  updated_at: ISODate()
}

// wager_history collection
{
  _id: ObjectId,
  user_id: "user-123",
  bonus_id: ObjectId,
  amount: 10,
  game_id: "game-456",
  timestamp: ISODate()
}
```

**Pros:**
- Clean separation of concerns
- Easy to query individual aspects
- Flexible for future changes

**Cons:**
- Multiple queries for full picture
- Join operations needed
- More complex updates

**Query Performance:** Medium
**Storage Efficiency:** High

### Option 2: Embedded Documents
```javascript
// user_bonuses collection
{
  _id: "user-123",
  bonuses: [{
    id: "welcome-bonus",
    type: "welcome",
    amount: 1000,
    wagering_required: 2000,
    wagering_completed: 500,
    status: "active",
    created_at: ISODate(),
    wager_history: [{
      amount: 10,
      game_id: "game-456",
      timestamp: ISODate()
    }]
  }],
  real_balance: 0,
  bonus_balance: 1000
}
```

**Pros:**
- Single query for all user data
- Atomic updates
- Great read performance

**Cons:**
- Document size limits (16MB)
- Difficult to query across users
- Array updates can be slow

**Query Performance:** High (for single user)
**Storage Efficiency:** Low (duplication)

### Option 3: Hybrid Approach
```javascript
// user_bonuses collection (main state)
{
  _id: "user-123",
  active_bonus: {
    id: "welcome-bonus",
    type: "welcome",
    amount: 1000,
    wagering_required: 2000,
    wagering_completed: 500,
    status: "active",
    created_at: ISODate()
  },
  real_balance: 0,
  bonus_balance: 1000,
  total_balance: 1000,
  version: 1  // for optimistic locking
}

// wager_history collection (audit trail)
{
  _id: ObjectId,
  user_id: "user-123",
  bonus_id: "welcome-bonus",
  amount: 10,
  type: "bonus",  // or "real"
  game_id: "game-456",
  balance_before: 1000,
  balance_after: 990,
  timestamp: ISODate()
}

// bonus_archive collection (completed/expired)
{
  _id: ObjectId,
  user_id: "user-123",
  bonus: { /* full bonus data */ },
  completed_at: ISODate(),
  total_wagered: 2000
}
```

**Pros:**
- Fast queries for active state
- Complete audit trail
- Handles large history well
- Supports analytics

**Cons:**
- More collections to manage
- Some data duplication
- Multiple updates needed

**Query Performance:** High
**Storage Efficiency:** Medium

## Decision: Option 3 - Hybrid Approach

### Rationale
1. **Performance**: O(1) lookups for active bonus state
2. **Audit Trail**: Complete history in separate collection
3. **Scalability**: Wager history won't bloat main document
4. **Analytics**: Easy to run aggregations on history
5. **Sentry Benefits**: Clear boundaries for transaction monitoring

## Detailed Schema Design

### 1. user_bonuses Collection
```javascript
{
  _id: "user-123",  // Use user_id as _id for fast lookup
  
  // Active bonus (only one at a time for simplicity)
  active_bonus: {
    id: "welcome-bonus-2025-01-07",
    type: "welcome",
    amount: 1000.00,
    wagering_required: 2000.00,
    wagering_completed: 0.00,
    progress_percentage: 0.0,
    status: "active",  // active, completed, expired
    created_at: ISODate("2025-01-07T10:00:00Z"),
    expires_at: null,  // No expiration for POC
    last_updated: ISODate("2025-01-07T10:00:00Z")
  },
  
  // Balance tracking
  real_balance: 0.00,
  bonus_balance: 1000.00,
  total_balance: 1000.00,  // Denormalized for performance
  
  // Metadata
  total_bonuses_claimed: 1,
  total_bonuses_completed: 0,
  lifetime_wagered: 0.00,
  
  // Concurrency control
  version: 1,
  last_wager_time: null,
  
  // Indexes: _id (primary)
}
```

### 2. wager_history Collection
```javascript
{
  _id: ObjectId("..."),
  user_id: "user-123",
  
  // Wager details
  wager_id: "wager-2025-01-07-001",
  game_id: "game-456",
  game_result: "lose",  // win, lose
  
  // Amount details
  wager_amount: 10.00,
  bonus_used: 10.00,
  real_used: 0.00,
  payout: 0.00,
  
  // Bonus tracking
  bonus_id: "welcome-bonus-2025-01-07",
  wagering_progress_before: 0.00,
  wagering_progress_after: 10.00,
  
  // Balance snapshot
  balance_snapshot: {
    real_before: 0.00,
    real_after: 0.00,
    bonus_before: 1000.00,
    bonus_after: 990.00,
    total_before: 1000.00,
    total_after: 990.00
  },
  
  // Metadata
  timestamp: ISODate("2025-01-07T10:05:00Z"),
  processing_time_ms: 45,
  
  // Sentry trace
  trace_id: "abc123...",
  span_id: "def456...",
  
  // Indexes: user_id + timestamp (compound), bonus_id
}
```

### 3. bonus_conversions Collection
```javascript
{
  _id: ObjectId("..."),
  user_id: "user-123",
  bonus_id: "welcome-bonus-2025-01-07",
  
  // Conversion details
  bonus_amount: 1000.00,
  total_wagered: 2000.00,
  conversion_rate: 1.0,  // 100% converted
  
  // Timeline
  bonus_created_at: ISODate("2025-01-07T10:00:00Z"),
  conversion_completed_at: ISODate("2025-01-07T12:00:00Z"),
  duration_minutes: 120,
  
  // Stats
  total_wagers: 200,
  winning_wagers: 70,
  win_rate: 0.35,
  
  // Indexes: user_id, conversion_completed_at
}
```

## MongoDB Indexes

```javascript
// Optimize for common queries
db.user_bonuses.createIndex({ "_id": 1 })  // Primary key

db.wager_history.createIndex({ "user_id": 1, "timestamp": -1 })
db.wager_history.createIndex({ "bonus_id": 1 })
db.wager_history.createIndex({ "trace_id": 1 })  // For Sentry correlation

db.bonus_conversions.createIndex({ "user_id": 1 })
db.bonus_conversions.createIndex({ "conversion_completed_at": -1 })
```

## Query Patterns

### 1. Get User Balance (Most Common)
```javascript
db.user_bonuses.findOne({ _id: "user-123" })
// O(1) with primary key
```

### 2. Check Wagering Progress
```javascript
db.user_bonuses.findOne(
  { _id: "user-123" },
  { "active_bonus.wagering_completed": 1, "active_bonus.wagering_required": 1 }
)
// O(1) with projection
```

### 3. Get Recent Wagers
```javascript
db.wager_history.find({ user_id: "user-123" })
  .sort({ timestamp: -1 })
  .limit(10)
// O(log n) with index
```

### 4. Analytics: Daily Wagering Volume
```javascript
db.wager_history.aggregate([
  {
    $match: {
      timestamp: {
        $gte: ISODate("2025-01-07T00:00:00Z"),
        $lt: ISODate("2025-01-08T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: null,
      total_volume: { $sum: "$wager_amount" },
      total_wagers: { $sum: 1 },
      unique_users: { $addToSet: "$user_id" }
    }
  }
])
```

## Sentry Integration Points

### 1. Slow Query Detection
```php
$span = \Sentry\startSpan(['op' => 'db.query', 'description' => 'Get user bonus']);
$result = $this->collection->findOne(['_id' => $userId]);
$span->finish();
```

### 2. Transaction Monitoring
```php
$transaction = \Sentry\startTransaction(['name' => 'bonus.check_progress']);
// All DB operations within transaction
$transaction->finish();
```

### 3. Business Metrics
```php
\Sentry\metrics()->gauge(
    'bonus.wagering_progress',
    $bonus['wagering_completed'] / $bonus['wagering_required'],
    ['unit' => 'ratio', 'tags' => ['bonus_type' => 'welcome']]
);
```

## Data Consistency Strategy

### Atomic Operations
```javascript
// Update progress atomically
db.user_bonuses.updateOne(
  { _id: "user-123", "active_bonus.status": "active" },
  {
    $inc: { 
      "active_bonus.wagering_completed": 10,
      "bonus_balance": -10
    },
    $set: {
      "active_bonus.last_updated": new Date(),
      "active_bonus.progress_percentage": 0.5
    }
  }
)
```

### Two-Phase Commit (for critical operations)
```php
$session = $client->startSession();
$session->startTransaction();

try {
    // Update bonus
    $this->updateBonus($session);
    
    // Record history
    $this->recordHistory($session);
    
    // Update balances
    $this->updateBalances($session);
    
    $session->commitTransaction();
} catch (\Exception $e) {
    $session->abortTransaction();
    throw $e;
}
```