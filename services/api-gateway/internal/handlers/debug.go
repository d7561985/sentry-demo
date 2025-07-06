package handlers

import (
	"fmt"
	"runtime"
	
	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
)

// TriggerPanic - Enhanced panic handler with rich context for better Sentry debugging
func TriggerPanic() gin.HandlerFunc {
	return func(c *gin.Context) {
		userID := c.Param("userId")
		
		// Add breadcrumbs to track user actions leading to panic
		sentry.AddBreadcrumb(&sentry.Breadcrumb{
			Message:  fmt.Sprintf("User %s accessed panic endpoint", userID),
			Category: "debug",
			Level:    sentry.LevelInfo,
			Data: map[string]interface{}{
				"user_id": userID,
				"endpoint": c.Request.URL.Path,
				"method": c.Request.Method,
			},
		})
		
		// Trigger panic for specific user ID
		if userID == "panic-test" {
			// Set comprehensive context before panic
			if hub := sentry.GetHubFromContext(c.Request.Context()); hub != nil {
				hub.ConfigureScope(func(scope *sentry.Scope) {
					scope.SetUser(sentry.User{
						ID: userID,
						IPAddress: c.ClientIP(),
					})
					scope.SetTag("panic.type", "intentional")
					scope.SetTag("debug.trigger", "panic")
					
					// Add request context
					scope.SetContext("request", map[string]interface{}{
						"url":       c.Request.URL.String(),
						"method":    c.Request.Method,
						"userAgent": c.Request.UserAgent(),
						"clientIP":  c.ClientIP(),
					})
					
					// Add runtime context
					scope.SetContext("runtime", map[string]interface{}{
						"goroutines": runtime.NumGoroutine(),
						"memory":     getMemoryStats(),
						"cpu_count":  runtime.NumCPU(),
						"go_version": runtime.Version(),
					})
				})
			}
			
			// Create a rich panic message with context
			panicMsg := fmt.Sprintf(
				"[DEMO] Gateway panic triggered!\nUser: %s\nEndpoint: %s\nThis demonstrates enhanced error context in Go services.",
				userID,
				c.Request.URL.Path,
			)
			panic(panicMsg)
		}
		
		c.JSON(200, gin.H{
			"message": "No panic triggered",
			"userId":  userID,
		})
	}
}

// getMemoryStats returns current memory statistics
func getMemoryStats() map[string]interface{} {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	return map[string]interface{}{
		"alloc_mb":       float64(m.Alloc) / 1024 / 1024,
		"total_alloc_mb": float64(m.TotalAlloc) / 1024 / 1024,
		"sys_mb":         float64(m.Sys) / 1024 / 1024,
		"num_gc":         m.NumGC,
		"gc_cpu_percent": m.GCCPUFraction * 100,
	}
}