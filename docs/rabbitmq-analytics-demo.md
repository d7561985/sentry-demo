# RabbitMQ Analytics Integration Demo

## Overview

This demo showcases how Sentry provides end-to-end distributed tracing across asynchronous message queues, specifically demonstrating analytics data collection through RabbitMQ.

## Architecture

```
┌─────────────┐     Game Result      ┌──────────────┐      Consumer      ┌─────────────┐
│ Game Engine │───────Message──────▶│              │──────────────────▶│  Analytics  │
└─────────────┘                      │   RabbitMQ   │                    │   Service   │
                                     │              │                    └─────────────┘
┌─────────────┐   Payment Event      │   Exchange:  │                           │
│   Payment   │───────Message──────▶│    gaming    │                           ▼
│   Service   │                      │              │                    ┌─────────────┐
└─────────────┘                      │   Queues:    │                    │   MongoDB   │
                                     │  - analytics │                    │ Real-time   │
                                     │              │                    │    Stats    │
                                     └──────────────┘                    └─────────────┘
```

## Key Features Demonstrated

1. **Distributed Tracing Through Message Queues**
   - Trace context propagation from HTTP request → Service → RabbitMQ → Consumer
   - Full visibility of async processing latency
   - Message queue performance metrics

2. **Real-time Analytics Processing**
   - Game results and payment events processed asynchronously
   - Pre-aggregated statistics for instant queries
   - Decoupled analytics from main game flow

3. **Error Handling & Resilience**
   - Automatic reconnection on RabbitMQ failures
   - Message requeuing on processing errors
   - Non-blocking publishing (game continues if MQ is down)

## Demo Scenarios

### Scenario 1: End-to-End Trace Through Message Queue

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Access RabbitMQ Management UI**:
   - URL: http://localhost:15672
   - Username: admin
   - Password: password

3. **Play a game**:
   - Open frontend: http://localhost:4200
   - Click "Spin" to play
   - Check Sentry Performance dashboard

4. **Observe the trace**:
   - HTTP request from frontend
   - API Gateway processing
   - Game Engine calculation
   - **NEW**: RabbitMQ publish span
   - **NEW**: Consumer processing span
   - Analytics data update

### Scenario 2: Real-time Analytics Dashboard

1. **Check real-time analytics**:
   ```bash
   curl http://localhost:8084/api/v1/analytics/realtime/summary
   ```

2. **Play multiple games rapidly**:
   - Use the frontend to play 10-20 games
   - Watch the queues in RabbitMQ Management UI
   - Check analytics update in real-time

3. **Compare with traditional aggregation**:
   - Real-time endpoint: Instant results from pre-aggregated data
   - Daily stats endpoint: Slower aggregation query

### Scenario 3: Message Queue Resilience

1. **Stop the Analytics consumer**:
   ```bash
   docker-compose stop analytics-service
   ```

2. **Continue playing games**:
   - Games still work normally
   - Messages accumulate in RabbitMQ
   - Check queue depth in Management UI

3. **Restart Analytics**:
   ```bash
   docker-compose start analytics-service
   ```

4. **Observe catch-up processing**:
   - Consumer processes backlog
   - All traces maintain context
   - Analytics become current

### Scenario 4: Error Handling

1. **Simulate MongoDB failure**:
   ```bash
   docker-compose stop mongodb
   ```

2. **Observe behavior**:
   - Publishers continue to work (non-blocking)
   - Consumer retries with exponential backoff
   - Messages remain in queue
   - Errors captured in Sentry

3. **Restore MongoDB**:
   ```bash
   docker-compose start mongodb
   ```

## Performance Metrics

### Custom Sentry Tags & Measurements

- **Message Queue Tags**:
  - `mq.published`: Success/failure of publishing
  - `mq.queue`: Target queue name
  - `mq.routing_key`: Message routing key
  - `analytics.type`: Type of analytics event

- **Performance Measurements**:
  - Publishing latency
  - Consumer processing time
  - Queue depth (via RabbitMQ metrics)
  - Aggregation update time

## Talking Points for Demo

1. **Trace Continuity**:
   - "Notice how the trace continues seamlessly from HTTP request through the message queue to the consumer"
   - "Each span maintains the original trace ID, providing full visibility"

2. **Performance Impact**:
   - "Publishing to RabbitMQ adds minimal latency (typically <5ms)"
   - "Analytics processing is completely decoupled from user experience"

3. **Scalability**:
   - "Consumer can be scaled horizontally for high-volume processing"
   - "Pre-aggregation enables instant analytics queries"

4. **Reliability**:
   - "System remains operational even if analytics are down"
   - "Message persistence ensures no data loss"

## Configuration Details

### Environment Variables

- `RABBITMQ_URL`: Connection string for all services
- Default: `amqp://admin:password@rabbitmq:5672`

### Queue Configuration

- Exchange: `gaming` (topic exchange)
- Queues:
  - `analytics.game_results`: Game outcomes
  - `analytics.payments`: Payment events
- Routing Keys:
  - `game.result`: Game results
  - `payment.credit`: Credit transactions
  - `payment.debit`: Debit transactions

## Monitoring Best Practices

1. **Set up alerts for**:
   - Queue depth exceeding threshold
   - Consumer processing errors
   - Publishing failures

2. **Dashboard metrics**:
   - Messages published/consumed per minute
   - Average processing time
   - Error rate by queue

3. **Trace sampling**:
   - Consider reducing sample rate for high-volume MQ operations
   - Use dynamic sampling based on error status

## Troubleshooting

### Common Issues

1. **Consumer not processing messages**:
   - Check RabbitMQ connection in logs
   - Verify queue bindings in Management UI
   - Check for MongoDB connectivity

2. **Traces not connecting**:
   - Ensure trace headers are properly propagated
   - Check Sentry SDK versions compatibility
   - Verify `continue_trace` implementation

3. **High message latency**:
   - Check consumer prefetch count
   - Monitor MongoDB query performance
   - Consider consumer scaling

## Summary

This integration demonstrates how Sentry provides complete observability for asynchronous, event-driven architectures. The combination of distributed tracing, error tracking, and performance monitoring across message queues enables teams to maintain visibility and quickly resolve issues in complex microservice environments.