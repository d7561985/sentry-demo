package errors

import (
	"fmt"
	"runtime"
	"strings"

	"github.com/getsentry/sentry-go"
)

// SentryError is an error type that captures stack trace
type SentryError struct {
	message string
	cause   error
	stack   []uintptr
	context map[string]interface{}
}

// Error implements the error interface
func (e *SentryError) Error() string {
	if e.cause != nil {
		return fmt.Sprintf("%s: %v", e.message, e.cause)
	}
	return e.message
}

// StackTrace returns the stack trace for Sentry
func (e *SentryError) StackTrace() []uintptr {
	return e.stack
}

// Cause returns the underlying error
func (e *SentryError) Cause() error {
	return e.cause
}

// New creates a new error with stack trace
func New(message string) error {
	return &SentryError{
		message: message,
		stack:   captureStackTrace(),
		context: make(map[string]interface{}),
	}
}

// Wrap wraps an existing error with additional context and stack trace
func Wrap(err error, message string) error {
	if err == nil {
		return nil
	}
	return &SentryError{
		message: message,
		cause:   err,
		stack:   captureStackTrace(),
		context: make(map[string]interface{}),
	}
}

// WithContext adds context to the error
func WithContext(err error, key string, value interface{}) error {
	if sentryErr, ok := err.(*SentryError); ok {
		sentryErr.context[key] = value
		return sentryErr
	}
	// If not a SentryError, wrap it
	sentryErr := &SentryError{
		message: err.Error(),
		cause:   err,
		stack:   captureStackTrace(),
		context: map[string]interface{}{
			key: value,
		},
	}
	return sentryErr
}

// CaptureWithContext captures an error with additional context
func CaptureWithContext(err error, contexts ...map[string]interface{}) {
	if err == nil {
		return
	}

	sentry.WithScope(func(scope *sentry.Scope) {
		// Add stack trace if available
		if sentryErr, ok := err.(*SentryError); ok {
			// Add custom contexts
			for k, v := range sentryErr.context {
				scope.SetContext("error_context", map[string]interface{}{k: v})
			}
		}

		// Add additional contexts
		for _, ctx := range contexts {
			for key, value := range ctx {
				scope.SetContext(key, map[string]interface{}{"value": value})
			}
		}

		// Add breadcrumb
		scope.AddBreadcrumb(&sentry.Breadcrumb{
			Message:  err.Error(),
			Category: "error",
			Level:    sentry.LevelError,
		}, 10)

		sentry.CaptureException(err)
	})
}

// captureStackTrace captures the current stack trace
func captureStackTrace() []uintptr {
	const depth = 32
	var pcs [depth]uintptr
	n := runtime.Callers(3, pcs[:]) // Skip runtime.Callers, captureStackTrace and the wrapper
	return pcs[:n]
}

// RecoverWithContext recovers from panic and sends to Sentry with context
func RecoverWithContext(ctx map[string]interface{}) {
	if r := recover(); r != nil {
		sentry.WithScope(func(scope *sentry.Scope) {
			// Add panic context
			scope.SetContext("panic_context", ctx)
			
			// Add stack trace
			buf := make([]byte, 1024*8)
			n := runtime.Stack(buf, false)
			scope.SetContext("stack_trace", map[string]interface{}{
				"raw": string(buf[:n]),
			})

			// Capture based on type
			switch x := r.(type) {
			case error:
				sentry.CaptureException(x)
			case string:
				sentry.CaptureMessage(x)
			default:
				sentry.CaptureMessage(fmt.Sprintf("Unknown panic: %v", r))
			}
		})
	}
}

// FormatStackTrace formats a stack trace for logging
func FormatStackTrace(stack []uintptr) string {
	var sb strings.Builder
	frames := runtime.CallersFrames(stack)
	for {
		frame, more := frames.Next()
		sb.WriteString(fmt.Sprintf("%s\n\t%s:%d\n", frame.Function, frame.File, frame.Line))
		if !more {
			break
		}
	}
	return sb.String()
}