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

// ProxyToAnalytics forwards requests to the analytics service
func ProxyToAnalytics(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		span := sentry.StartSpan(c.Request.Context(), "gateway.proxy.analytics")
		defer span.Finish()

		// Get the full path after /api/v1/
		fullPath := c.Request.URL.Path
		// Extract the path after /api/v1/ to forward to analytics service
		pathAfterV1 := strings.TrimPrefix(fullPath, "/api/v1/")
		
		// Analytics service has some endpoints under /api/v1/ and some under /api/
		// Check if this is a debug endpoint
		var analyticsURL string
		if strings.HasPrefix(pathAfterV1, "analytics/debug/") {
			// Debug endpoints are under /api/debug/
			debugPath := strings.TrimPrefix(pathAfterV1, "analytics/")
			analyticsURL = fmt.Sprintf("http://analytics-service:8084/api/%s", debugPath)
		} else {
			// Regular endpoints are under /api/v1/
			analyticsURL = fmt.Sprintf("http://analytics-service:8084/api/v1/%s", pathAfterV1)
		}
		
		// Add query parameters if any
		if c.Request.URL.RawQuery != "" {
			analyticsURL += "?" + c.Request.URL.RawQuery
		}

		span.SetData("analytics.url", analyticsURL)
		span.SetData("method", c.Request.Method)

		// Create new request
		req, err := http.NewRequestWithContext(span.Context(), c.Request.Method, analyticsURL, c.Request.Body)
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
			c.JSON(http.StatusBadGateway, gin.H{"error": "Failed to reach analytics service"})
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