# Task Archive: Sentry Independent Traces Implementation

## Metadata
- **Complexity**: Level 2
- **Type**: Enhancement
- **Date Completed**: 2025-01-06
- **Related Tasks**: Sentry Session Replay Fix

## Summary
Successfully implemented independent transaction traces for the Angular frontend using Sentry SDK v9.35.0. Each user action now creates its own separate trace instead of being nested within pageload/navigation transactions. This allows for better analysis of specific business operations in the Sentry performance monitoring dashboard.

## Requirements
- Create independent traces for each user action (not nested in pageload)
- Fix infinite session replay recording issue
- Update all user interaction components to use new trace strategy
- Maintain proper error handling and transaction status

## Implementation
### Approach
After testing multiple approaches (forceTransaction, startNewTrace, parentSpan: null), discovered that only `Sentry.startNewTrace()` creates truly independent transactions in SDK v9.

### Key Components
- **sentry-traces.ts**: Utility module with helper functions
  - `createNewTrace()`: Main function for independent transactions
  - `TransactionNames`: Standardized naming constants
  - `Operations`: Transaction operation types
  - `setTransactionStatus()`: Helper for proper status codes

- **main.ts**: Updated Sentry configuration
  - Added `maxReplayDuration: 60000` to limit replay to 1 minute
  - Added `minReplayDuration: 5000` for minimum recording
  - Removed problematic `linkPreviousTrace` option

### Files Changed
- `/services/frontend/src/app/utils/sentry-traces.ts`: Created utility module
- `/services/frontend/src/main.ts`: Fixed replay configuration
- `/services/frontend/src/app/slot-machine/slot-machine.component.ts`: Updated all actions to use createNewTrace
- `/services/frontend/src/app/business-metrics/business-metrics.component.ts`: Updated metrics refresh
- `/services/frontend/src/app/app.component.ts`: Removed test component

## Testing
- ✅ Verified `startNewTrace` creates independent transactions
- ✅ Confirmed traces appear separately in Sentry UI
- ✅ Tested all debug methods create proper traces
- ✅ Verified replay recording stops at 1 minute
- ✅ Confirmed proper error handling with numeric status codes

## Lessons Learned
- **SDK Documentation Gap**: Sentry docs don't clearly explain that only `startNewTrace()` works for independent transactions
- **TypeScript Limitations**: Type definitions suggested features that don't work (e.g., options for startNewTrace)
- **Replay Configuration**: Default 60-minute replay duration can cause issues; explicit limits are necessary
- **Status Codes**: Must use numeric codes (1 for OK, 2 for ERROR) instead of strings in v9

## Future Considerations
- Monitor replay recordings to ensure 1-minute limit is appropriate
- Consider adding more custom attributes to traces for business insights
- Document trace naming conventions in project README
- Extend independent traces to navigation and form submissions
- Consider implementing trace sampling for high-traffic actions

## References
- [Reflection Document](/memory-bank/reflect-sentry-traces-2025-01-06.md)
- [Sentry SDK v9 Migration Guide](https://docs.sentry.io/platforms/javascript/migration/)
- [Original Task Definition](/memory-bank/tasks.md#task-implement-independent-sentry-traces-strategy)