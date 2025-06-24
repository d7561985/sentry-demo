# Scenario 4: Business Metrics Monitoring

## Overview
This scenario demonstrates how Sentry can track custom business metrics for an iGaming platform, providing real-time insights into key performance indicators (KPIs) that directly impact revenue and player satisfaction.

## Business Value
- **Real-time RTP monitoring**: Track Return to Player percentage to ensure game fairness
- **Session analytics**: Monitor player engagement and session duration
- **Financial insights**: Track revenue, deposits, and withdrawal patterns
- **Anomaly detection**: Automatic alerts for business metric anomalies

## Key Metrics Implemented

### 1. Gaming Metrics
- **RTP (Return to Player)**: Real-time and 24-hour rolling average
- **Win Rate**: Player win percentage tracking
- **Bet Volume**: Total betting volume monitoring
- **Active Sessions**: Current player engagement

### 2. Financial Metrics
- **Net Revenue**: House edge and profitability
- **Payment Success Rate**: Transaction reliability
- **Deposit/Withdrawal Ratio**: Cash flow monitoring
- **Average Bet Size**: Player behavior insights

### 3. Player Behavior
- **Session Duration**: Engagement tracking
- **Games per Session**: Activity intensity
- **Player Lifetime Value**: Long-term profitability

## Implementation Details

### Custom Metrics Module
Created shared business metrics module (`metrics.py` / `metrics.js`) with:
- Standardized metric names and units
- Automatic anomaly detection
- Sentry measurement integration
- Business-focused transactions

### Service Integration

#### Game Engine
- Tracks RTP per game and session
- Monitors win rates and bet volumes
- Calculates rolling 24-hour RTP
- Detects RTP anomalies (< 85% or > 98%)

#### Payment Service
- Tracks financial transactions
- Monitors payment success rates
- Calculates net revenue
- Detects negative revenue patterns

#### Analytics Service
- Aggregates business metrics
- Provides real-time dashboards
- Calculates player engagement metrics
- Exposes REST endpoints for metrics

#### Frontend
- Business metrics dashboard at `/metrics`
- Real-time metric visualization
- Demo scenario triggers
- Auto-refresh every 30 seconds

## Demo Scenarios

### 1. RTP Anomaly
Trigger: `POST /api/v1/game-engine/business-metrics`
```json
{
  "scenario": "rtp_anomaly"
}
```
- Simulates RTP dropping to 75% (critical)
- Also shows RTP at 99.5% (warning)
- Generates Sentry alerts

### 2. Session Surge
Trigger: `POST /api/v1/game-engine/business-metrics`
```json
{
  "scenario": "session_surge"
}
```
- Normal: 150 active sessions
- Surge: 850 active sessions
- Useful for capacity planning

### 3. Win Rate Manipulation
Trigger: `POST /api/v1/game-engine/business-metrics`
```json
{
  "scenario": "win_rate_manipulation"
}
```
- Simulates 85% win rate (fraud indicator)
- Triggers critical alert

### 4. Payment Failures
Trigger: `POST /api/v1/payment/financial-metrics`
```json
{
  "scenario": "payment_failure_spike"
}
```
- Drops success rate to 85%
- Generates multiple error events

### 5. Revenue Anomaly
Trigger: `POST /api/v1/payment/financial-metrics`
```json
{
  "scenario": "revenue_anomaly"
}
```
- Shows negative daily revenue
- Unusual deposit/withdrawal ratio

## API Endpoints

### Analytics Service Endpoints

1. **RTP Metrics**
   ```
   GET /api/v1/business-metrics/rtp?hours=24
   ```
   Returns overall RTP, hourly breakdown, and player rankings

2. **Active Sessions**
   ```
   GET /api/v1/business-metrics/active-sessions
   ```
   Returns current sessions, duration distribution, and engagement metrics

3. **Financial Summary**
   ```
   GET /api/v1/business-metrics/financial-summary?days=7
   ```
   Returns revenue, transaction volumes, and financial health

## Sentry Configuration

### Custom Measurements
```python
# Game metrics
sentry_sdk.set_measurement("business.rtp", 95.5, "percent")
sentry_sdk.set_measurement("business.bet_volume", 10000, "currency")
sentry_sdk.set_measurement("business.active_sessions", 250, "none")

# Financial metrics
sentry_sdk.set_measurement("business.revenue.net", 2500, "currency")
sentry_sdk.set_measurement("business.payment.success_rate", 98.5, "percent")
```

### Business Transactions
```python
transaction = BusinessMetrics.start_business_transaction(
    name="calculate_daily_rtp",
    op="business"
)
transaction.set_tag("transaction.business", "true")
```

### Anomaly Alerts
- RTP outside 85-98% range
- Win rate above 50%
- Payment success rate below 95%
- Negative revenue detection

## Testing Instructions

1. **Access Business Metrics Dashboard**
   ```
   http://localhost:4200/metrics
   ```

2. **Generate Game Activity**
   - Play slot machine to generate RTP data
   - Check metrics update in real-time

3. **Trigger Demo Scenarios**
   - Use buttons in debug panel
   - Watch for Sentry alerts

4. **View in Sentry**
   - Custom measurements in transaction details
   - Business metric anomaly alerts
   - Performance monitoring dashboard

## Benefits Demonstrated

1. **Reduced MTTR**: Business anomalies detected immediately
2. **Proactive Monitoring**: Issues identified before player complaints
3. **Data-Driven Decisions**: Real-time business intelligence
4. **Regulatory Compliance**: RTP tracking for gaming regulations
5. **Revenue Protection**: Fraud and anomaly detection

## Next Steps

1. Configure Sentry dashboards for business metrics
2. Set up alert rules for anomaly thresholds
3. Create custom reports for stakeholders
4. Integrate with business intelligence tools
</content>