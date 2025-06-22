package handlers

import (
	"github.com/gin-gonic/gin"
)

// TriggerPanic - for Scenario 2 demo
func TriggerPanic() gin.HandlerFunc {
	return func(c *gin.Context) {
		userID := c.Param("userId")
		
		// Trigger panic for specific user ID
		if userID == "panic-test" {
			panic("Demo panic for Sentry")
		}
		
		c.JSON(200, gin.H{
			"message": "No panic triggered",
			"userId":  userID,
		})
	}
}