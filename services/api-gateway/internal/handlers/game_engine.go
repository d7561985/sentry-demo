package handlers

import (
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/sentry-poc/api-gateway/internal/config"
)

// ProxyToGameEngine forwards requests to the game engine service
func ProxyToGameEngine(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		span := sentry.StartSpan(c.Request.Context(), "gateway.proxy.game-engine")
		defer span.Finish()

		// Get the full path after /api/v1/
		fullPath := c.Request.URL.Path
		// Extract the path after /api/v1/game-engine/ to forward to game engine service
		pathAfterV1 := strings.TrimPrefix(fullPath, "/api/v1/game-engine/")
		gameEngineURL := fmt.Sprintf("%s/%s", cfg.GameServiceURL, pathAfterV1)
		
		// Add query parameters if any
		if c.Request.URL.RawQuery != "" {
			gameEngineURL += "?" + c.Request.URL.RawQuery
		}

		span.SetData("game_engine.url", gameEngineURL)
		span.SetData("method", c.Request.Method)

		// Create new request
		req, err := http.NewRequestWithContext(span.Context(), c.Request.Method, gameEngineURL, c.Request.Body)
		if err != nil {
			span.Status = sentry.SpanStatusInternalError
			sentry.CaptureException(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
			return
		}

		// Copy headers
		for key, values := range c.Request.Header {
			for _, value := range values {
				req.Header.Add(key, value)
			}
		}

		// Add Sentry trace headers for propagation
		if span != nil {
			req.Header.Set("Sentry-Trace", span.ToSentryTrace())
			// Add baggage header for dynamic sampling context
			if baggage := span.ToBaggage(); baggage != "" {
				req.Header.Set("Baggage", baggage)
			}
		}

		// Make request
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			span.Status = sentry.SpanStatusInternalError
			sentry.CaptureException(err)
			c.JSON(http.StatusBadGateway, gin.H{"error": "Failed to reach game engine service"})
			return
		}
		defer resp.Body.Close()

		// Copy response
		span.SetData("response.status", resp.StatusCode)
		if resp.StatusCode >= 400 {
			span.Status = sentry.SpanStatusInternalError
		}

		// Copy response headers
		for key, values := range resp.Header {
			for _, value := range values {
				c.Header(key, value)
			}
		}

		// Copy response body
		c.Status(resp.StatusCode)
		io.Copy(c.Writer, resp.Body)
	}
}