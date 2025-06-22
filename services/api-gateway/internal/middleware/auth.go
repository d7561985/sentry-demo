package middleware

import (
	"net/http"
	"strings"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
)

// Simple JWT auth middleware for demo
func Auth() gin.HandlerFunc {
	return func(c *gin.Context) {
		// For demo purposes, we'll create a simple token
		// In real app, this would validate a proper JWT
		authHeader := c.GetHeader("Authorization")
		
		// If no auth header, create a demo user
		if authHeader == "" {
			userId := c.GetHeader("X-User-ID")
			if userId == "" {
				userId = "demo-user"
			}
			
			// Set user context for Sentry
			if hub := sentry.GetHubFromContext(c.Request.Context()); hub != nil {
				hub.ConfigureScope(func(scope *sentry.Scope) {
					scope.SetUser(sentry.User{
						ID:       userId,
						Username: "demo_player",
					})
				})
			}
			
			c.Set("userId", userId)
			c.Next()
			return
		}

		// Simple token validation
		tokenString := strings.Replace(authHeader, "Bearer ", "", 1)
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			// Demo secret
			return []byte("demo-secret"), nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		// Extract claims
		if claims, ok := token.Claims.(jwt.MapClaims); ok {
			userId := claims["user_id"].(string)
			c.Set("userId", userId)
			
			// Set user context for Sentry
			if hub := sentry.GetHubFromContext(c.Request.Context()); hub != nil {
				hub.ConfigureScope(func(scope *sentry.Scope) {
					scope.SetUser(sentry.User{
						ID:       userId,
						Username: claims["username"].(string),
					})
				})
			}
		}

		c.Next()
	}
}