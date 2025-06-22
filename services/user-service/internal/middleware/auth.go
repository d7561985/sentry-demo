package middleware

import (
	"net/http"
	"strings"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
)

// AuthMiddleware checks for valid authorization token
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		
		// Check if Authorization header is present
		if authHeader == "" {
			// No auth header - allow request to proceed (backward compatibility)
			c.Next()
			return
		}
		
		// Check Bearer token format
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			sentry.CaptureMessage("Invalid authorization header format")
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authorization header format",
			})
			c.Abort()
			return
		}
		
		token := parts[1]
		
		// Demo: Check for specific invalid token
		if token == "invalid-token" {
			// Capture auth error in Sentry with context
			sentry.WithScope(func(scope *sentry.Scope) {
				scope.SetTag("error_type", "authentication")
				scope.SetTag("auth_failure_reason", "invalid_token")
				scope.SetContext("auth", map[string]interface{}{
					"token": "invalid-token",
					"user_agent": c.GetHeader("User-Agent"),
					"ip": c.ClientIP(),
				})
				sentry.CaptureMessage("Authentication failed: Invalid token")
			})
			
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid or expired token",
				"code": "AUTH_FAILED",
			})
			c.Abort()
			return
		}
		
		// In a real app, you would validate the token here
		// For demo purposes, any other token is valid
		c.Next()
	}
}