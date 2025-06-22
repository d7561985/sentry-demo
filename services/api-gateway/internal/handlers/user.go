package handlers

import (
	"fmt"
	"net/http"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/sentry-poc/api-gateway/internal/config"
)

func GetUserBalance(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		span := sentry.TransactionFromContext(ctx)
		if span != nil {
			span.Name = "GET /api/v1/users/:userId/balance"
		}

		userID := c.Param("userId")

		// Create HTTP client with Sentry transport
		client := &http.Client{
			Timeout:   10 * time.Second,
			Transport: &sentryRoundTripper{},
		}

		// Forward to user service
		userSpan := sentry.StartSpan(ctx, "http.client", sentry.WithDescription("GET user-service:/users/:userId/balance"))
		userCtx := userSpan.Context()
		defer userSpan.Finish()

		url := fmt.Sprintf("http://user-service:8084/users/%s/balance", userID)
		httpReq, err := http.NewRequestWithContext(userCtx, "GET", url, nil)
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to create request"})
			return
		}

		resp, err := client.Do(httpReq)
		if err != nil {
			userSpan.Status = sentry.SpanStatusInternalError
			sentry.CaptureException(err)
			c.JSON(500, gin.H{"error": "User service unavailable"})
			return
		}
		defer resp.Body.Close()

		// Forward the response
		c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
	}
}