# Go + Sentry Best Practices Guide

This guide covers best practices for using Sentry with Go services to get maximum debugging value from error reports.

## Table of Contents
- [The Problem with Go Errors](#the-problem-with-go-errors)
- [Essential Configuration](#essential-configuration)
- [Error Handling Best Practices](#error-handling-best-practices)
- [Panic Recovery](#panic-recovery)
- [Context and Breadcrumbs](#context-and-breadcrumbs)
- [Goroutine Safety](#goroutine-safety)
- [Performance Considerations](#performance-considerations)
- [Testing Error Handling](#testing-error-handling)

## The Problem with Go Errors

Unlike languages like Python or JavaScript, Go's native errors are simple strings without stack traces. This makes debugging production issues challenging. Here's how to fix it:

### Before (Poor Context)
```go
if err != nil {
    sentry.CaptureException(err)
    return err
}
```
Result in Sentry: Just an error message, no context, no stack trace.

### After (Rich Context)
```go
if err != nil {
    sentry.WithScope(func(scope *sentry.Scope) {
        scope.SetContext("database", map[string]interface{}{
            "query": query,
            "params": params,
            "duration_ms": time.Since(start).Milliseconds(),
        })
        sentry.CaptureException(fmt.Errorf("database query failed: %w", err))
    })
    return err
}
```
Result in Sentry: Full context, wrapped error message, and stack trace.

## Essential Configuration

### 1. Always Enable Stack Traces

```go
sentry.Init(sentry.ClientOptions{
    Dsn:              "your-dsn",
    AttachStacktrace: true,  // Critical for Go!
    Environment:      "production",
    Release:          "myapp@1.0.0",
    SampleRate:       1.0,    // Capture 100% of errors
    TracesSampleRate: 0.1,    // Sample 10% of transactions
    MaxBreadcrumbs:   100,    // Keep more breadcrumbs
})
```

### 2. Use BeforeSend for Global Context

```go
sentry.Init(sentry.ClientOptions{
    // ... other options ...
    BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
        // Add runtime context to all errors
        event.Contexts["runtime"] = map[string]interface{}{
            "goroutines": runtime.NumGoroutine(),
            "memory_mb": getMemoryMB(),
        }
        
        // Improve fingerprinting
        if event.Exception != nil && len(event.Exception) > 0 {
            event.Fingerprint = append(event.Fingerprint, event.Exception[0].Type)
        }
        
        return event
    },
})
```

## Error Handling Best Practices

### 1. Create Errors with Stack Traces

Since Go 1.13, use `fmt.Errorf` with `%w` verb:

```go
func processUser(userID string) error {
    user, err := db.GetUser(userID)
    if err != nil {
        // Wraps error and preserves stack trace
        return fmt.Errorf("failed to get user %s: %w", userID, err)
    }
    
    if err := validateUser(user); err != nil {
        // Add context while wrapping
        return fmt.Errorf("user validation failed for %s: %w", userID, err)
    }
    
    return nil
}
```

### 2. Use Custom Error Types for Rich Context

```go
type DatabaseError struct {
    Query      string
    Params     []interface{}
    Duration   time.Duration
    Underlying error
}

func (e *DatabaseError) Error() string {
    return fmt.Sprintf("database error: %v (query took %v)", e.Underlying, e.Duration)
}

func (e *DatabaseError) Unwrap() error {
    return e.Underlying
}

// Usage
err := &DatabaseError{
    Query:      "SELECT * FROM users WHERE id = ?",
    Params:     []interface{}{userID},
    Duration:   time.Since(start),
    Underlying: originalErr,
}
sentry.CaptureException(err)
```

### 3. Add Context When Capturing

```go
func handleRequest(w http.ResponseWriter, r *http.Request) {
    defer func() {
        if err := recover(); err != nil {
            sentry.WithScope(func(scope *sentry.Scope) {
                scope.SetRequest(r)
                scope.SetUser(sentry.User{
                    ID:        getUserID(r),
                    IPAddress: r.RemoteAddr,
                })
                sentry.CurrentHub().Recover(err)
            })
            http.Error(w, "Internal Server Error", 500)
        }
    }()
    
    // Your handler logic...
}
```

## Panic Recovery

### 1. Enhanced Panic Recovery

```go
func RecoverWithContext(ctx context.Context, details map[string]interface{}) {
    if r := recover(); r != nil {
        hub := sentry.GetHubFromContext(ctx)
        if hub == nil {
            hub = sentry.CurrentHub()
        }
        
        hub.WithScope(func(scope *sentry.Scope) {
            // Add panic details
            scope.SetContext("panic_details", details)
            
            // Add stack trace
            buf := make([]byte, 1<<16)
            n := runtime.Stack(buf, true)
            scope.SetContext("full_stack", map[string]interface{}{
                "trace": string(buf[:n]),
            })
            
            // Recover based on type
            switch x := r.(type) {
            case error:
                hub.RecoverWithContext(ctx, x)
            case string:
                hub.RecoverWithContext(ctx, errors.New(x))
            default:
                hub.RecoverWithContext(ctx, fmt.Errorf("panic: %v", x))
            }
        })
    }
}
```

### 2. Middleware for Gin

```go
func SentryRecovery() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                hub := sentry.GetHubFromContext(c.Request.Context())
                if hub != nil {
                    hub.WithScope(func(scope *sentry.Scope) {
                        scope.SetRequest(c.Request)
                        scope.SetUser(sentry.User{
                            ID:        c.GetString("userID"),
                            IPAddress: c.ClientIP(),
                        })
                        scope.SetContext("gin", map[string]interface{}{
                            "path":   c.FullPath(),
                            "params": c.Params,
                        })
                        hub.Recover(err)
                    })
                }
                c.AbortWithStatus(500)
            }
        }()
        c.Next()
    }
}
```

## Context and Breadcrumbs

### 1. Add Breadcrumbs for User Actions

```go
func (h *Handler) CreateOrder(ctx context.Context, req *CreateOrderRequest) error {
    // Add breadcrumb for debugging trail
    sentry.AddBreadcrumb(&sentry.Breadcrumb{
        Message:  "Creating order",
        Category: "order",
        Level:    sentry.LevelInfo,
        Data: map[string]interface{}{
            "user_id":    req.UserID,
            "product_id": req.ProductID,
            "amount":     req.Amount,
        },
    })
    
    // Validate request
    if err := h.validateOrder(req); err != nil {
        sentry.AddBreadcrumb(&sentry.Breadcrumb{
            Message:  "Order validation failed",
            Category: "order",
            Level:    sentry.LevelWarning,
            Data:     map[string]interface{}{"error": err.Error()},
        })
        return err
    }
    
    // Process order...
}
```

### 2. Scope Management

```go
func ProcessBatch(items []Item) error {
    for i, item := range items {
        // Create a new scope for each item
        err := sentry.WithScope(func(scope *sentry.Scope) error {
            scope.SetTag("batch.index", fmt.Sprintf("%d", i))
            scope.SetContext("item", map[string]interface{}{
                "id":   item.ID,
                "type": item.Type,
            })
            
            if err := processItem(item); err != nil {
                sentry.CaptureException(err)
                return err
            }
            return nil
        })
        
        if err != nil {
            return fmt.Errorf("failed to process item %d: %w", i, err)
        }
    }
    return nil
}
```

## Goroutine Safety

### 1. Clone Hub for Goroutines

```go
func ProcessAsync(items []Item) {
    // Clone hub for goroutine safety
    hub := sentry.CurrentHub().Clone()
    
    go func() {
        // Use the cloned hub
        defer hub.Recover(nil)
        
        hub.ConfigureScope(func(scope *sentry.Scope) {
            scope.SetTag("processing.type", "async")
            scope.SetTag("goroutine.id", fmt.Sprintf("%d", getGoroutineID()))
        })
        
        for _, item := range items {
            if err := processItem(item); err != nil {
                hub.CaptureException(err)
            }
        }
    }()
}
```

### 2. Context Propagation

```go
func HandleConcurrent(ctx context.Context, tasks []Task) error {
    g, gctx := errgroup.WithContext(ctx)
    
    for _, task := range tasks {
        task := task // capture loop variable
        g.Go(func() error {
            // Clone hub with context
            hub := sentry.GetHubFromContext(gctx)
            if hub == nil {
                hub = sentry.CurrentHub()
            }
            hub = hub.Clone()
            
            defer hub.Recover(nil)
            
            hub.ConfigureScope(func(scope *sentry.Scope) {
                scope.SetContext("task", map[string]interface{}{
                    "id":   task.ID,
                    "type": task.Type,
                })
            })
            
            return processTask(gctx, task)
        })
    }
    
    return g.Wait()
}
```

## Performance Considerations

### 1. Sampling in Production

```go
sentry.Init(sentry.ClientOptions{
    // ... other options ...
    
    // Sample errors based on type
    BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
        // Always send critical errors
        if event.Level == sentry.LevelFatal || event.Level == sentry.LevelError {
            return event
        }
        
        // Sample warnings
        if event.Level == sentry.LevelWarning && rand.Float32() > 0.1 {
            return nil // Drop 90% of warnings
        }
        
        return event
    },
    
    // Dynamic trace sampling
    TracesSampler: func(ctx sentry.SamplingContext) float64 {
        // Higher sampling for critical endpoints
        if ctx.Span.Op == "http.server" {
            if strings.Contains(ctx.Span.Description, "/api/payment") {
                return 1.0 // 100% for payment endpoints
            }
            if strings.Contains(ctx.Span.Description, "/health") {
                return 0.01 // 1% for health checks
            }
        }
        return 0.1 // 10% default
    },
})
```

### 2. Efficient Context Addition

```go
// Bad: Creating new maps for each error
scope.SetContext("request", map[string]interface{}{
    "big_body": request.Body, // Don't send large payloads
})

// Good: Send only essential data
scope.SetContext("request", map[string]interface{}{
    "method":     request.Method,
    "path":       request.URL.Path,
    "size_bytes": len(request.Body),
    "user_id":    extractUserID(request),
})
```

## Testing Error Handling

### 1. Test Helper for Sentry

```go
func TestWithSentry(t *testing.T) {
    // Create test transport
    transport := &testTransport{}
    client, _ := sentry.NewClient(sentry.ClientOptions{
        Transport: transport,
    })
    hub := sentry.NewHub(client, sentry.NewScope())
    
    // Run test with custom hub
    hub.WithScope(func(scope *sentry.Scope) {
        // Your test code
        err := YourFunction()
        assert.Error(t, err)
        
        // Verify Sentry captured the error
        assert.Len(t, transport.events, 1)
        assert.Equal(t, "expected error message", transport.events[0].Message)
    })
}
```

### 2. Benchmark Error Handling

```go
func BenchmarkErrorCapture(b *testing.B) {
    // Setup
    sentry.Init(sentry.ClientOptions{
        Dsn:       "",  // Empty DSN for benchmarking
        Transport: &sentry.HTTPTransport{}, 
    })
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        sentry.WithScope(func(scope *sentry.Scope) {
            scope.SetTag("benchmark", "true")
            sentry.CaptureException(errors.New("benchmark error"))
        })
    }
}
```

## Summary

Key takeaways for better Go error handling with Sentry:

1. **Always enable `AttachStacktrace: true`** - This is critical for Go
2. **Wrap errors with context** using `fmt.Errorf("context: %w", err)`
3. **Use scopes** to add request-specific context
4. **Add breadcrumbs** to track user actions
5. **Clone hubs for goroutines** to ensure thread safety
6. **Rich panic recovery** with full context
7. **Sample intelligently** in production to control costs
8. **Test your error handling** to ensure it works as expected

With these practices, your Go services will provide error reports as rich and useful as those from Python or Node.js applications!