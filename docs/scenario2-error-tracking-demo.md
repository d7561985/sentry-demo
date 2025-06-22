# Scenario 2: Error Tracking Suite Demo

This demo showcases different types of errors across the iGaming platform and how Sentry captures, groups, and provides context for each error type.

## Setup

1. Ensure all services are running:
```bash
./start.sh
```

2. Open the frontend in your browser:
```
http://localhost:4200
```

3. Open your Sentry dashboard in another tab

## Error Scenarios

### 1. Frontend JavaScript Errors

#### A. Unhandled Promise Rejection
1. Click "🐛 Show Debug Panel" at the bottom of the slot machine
2. Click "💥 Trigger Promise Rejection"
3. Check browser console - you'll see the unhandled rejection
4. Check Sentry dashboard - the error appears with:
   - Full stack trace
   - User context
   - Browser information
   - Breadcrumbs leading to the error

#### B. Angular Component Error
1. In the debug panel, click "🔥 Trigger Component Error"
2. The error is caught by Angular's ErrorHandler
3. Check Sentry dashboard - the error appears with:
   - Custom context added by our ErrorHandler
   - Component information
   - Angular-specific tags

### 2. Backend Service Errors

#### A. Gateway Panic (Go)
1. In the debug panel, click "⚠️ Trigger Gateway Panic"
2. The gateway service will panic (but recover)
3. Check Sentry dashboard - you'll see:
   - Go panic stack trace
   - Recovery information
   - Request context

#### B. 401 Authentication Error
1. In the debug panel, click "🔒 Trigger 401 Auth Error"
2. The user service will reject the invalid token
3. Check Sentry dashboard - you'll see:
   - Authentication failure event
   - Token information (redacted)
   - Request metadata

### 3. Existing Random Errors

#### Payment Service Failures
- The payment service has a 10% random failure rate
- Play the slot machine multiple times
- Eventually you'll see payment failures in Sentry
- These errors include distributed trace context

## What to Look for in Sentry

### Error Grouping
- Sentry automatically groups similar errors
- Each error type has its own issue
- Error frequency and user impact are tracked

### Error Context
- User information (ID, username)
- Browser/platform details
- Custom tags and context we added
- Breadcrumbs showing user actions

### Distributed Tracing
- Errors maintain trace context
- You can see the full request flow
- Related errors across services are linked

### Performance Impact
- Errors show performance impact
- Transaction data is preserved
- You can correlate errors with slowdowns

## Testing the Full Flow

1. Start with a normal game spin to verify tracing works
2. Trigger each error type using the debug panel
3. Play several games to trigger random payment failures
4. Check Sentry to see all errors properly captured

## Key Benefits Demonstrated

1. **Reduced MTTR**: All error context in one place
2. **Error Prioritization**: See which errors affect most users
3. **Root Cause Analysis**: Full stack traces and context
4. **Proactive Monitoring**: Catch errors before users report them
5. **Cross-Service Visibility**: Errors linked across microservices

## Notes

- The debug panel is for demo purposes only
- In production, these errors would occur naturally
- Sentry's error tracking works without any user action
- All errors maintain distributed trace context from Scenario 1