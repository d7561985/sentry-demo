# Test Scenario 1: Distributed Tracing

## Prerequisites
1. Configure Sentry DSNs in `.env` file
2. Start all services: `./start.sh`
3. Open Sentry dashboard in browser

## Test Steps

### 1. Basic Trace Flow
1. Open http://localhost:4200
2. Click "SPIN" button
3. Go to Sentry → Performance → Transactions
4. Find the `slot-machine-spin` transaction
5. Click to see the full trace

**What to observe:**
- Complete trace from Frontend → Gateway → User → Game → Payment
- Each service adds its span to the trace
- Performance timings for each service

### 2. Intentional Performance Issues

**Slow Database Query (User Service)**
- Look for span: `db.query` with 500ms+ duration
- Description: "Find user by ID"
- Simulates missing MongoDB index

**N+1 Query Problem (User Service)**
- Add `?include_history=true` to demonstrate
- Look for multiple `db.query.game` spans
- Shows inefficient query pattern

**CPU Spike (Game Engine)**
- Look for span: `game.rng` 
- High duration due to inefficient calculation
- Check CPU profiling data if available

**Slow External API (Payment Service)**
- Look for span: `http.client` "External payment provider API"
- Duration: 2-5 seconds (random)
- Simulates slow third-party integration

### 3. Error Scenarios

**Payment Failures (10% rate)**
- Keep clicking SPIN until you get an error
- Check Sentry → Issues for "Payment provider timeout"
- Trace will show where the error occurred

**Panic Test (API Gateway)**
- Use curl or browser: http://localhost:8080/api/v1/debug/panic/panic-test
- Creates a panic in Go service
- Check how Sentry captures Go panics

### 4. Custom Metrics

In transaction details, check:
- `game.bet_amount` - Bet size
- `game.payout` - Win amount
- `payment.amount` - Transaction amount
- `payment.processing_time` - External API time

### 5. User Context

Each trace includes:
- User ID
- Session information
- Browser details (from Frontend)

## Verification Checklist

- [ ] Full trace visible with all 5 services
- [ ] Slow query visible in User Service (500ms+)
- [ ] CPU spike visible in Game Engine
- [ ] External API delay visible in Payment Service
- [ ] 10% of spins result in payment errors
- [ ] Custom measurements attached to traces
- [ ] User context properly propagated

## Troubleshooting

**No traces appearing:**
- Check `.env` has valid Sentry DSNs
- Verify all services are running: `docker-compose ps`
- Check service logs: `docker-compose logs [service-name]`

**Incomplete traces:**
- Ensure trace headers are propagated
- Check Sentry initialization in each service
- Verify `tracesSampleRate: 1.0` is set

**Services not responding:**
- Run `docker-compose logs` to check for errors
- Ensure MongoDB and Redis are running
- Check port conflicts on your system