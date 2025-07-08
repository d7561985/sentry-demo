package handlers

import (
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/sentry-poc/api-gateway/internal/config"
)

// ProxyToWager proxies requests to the wager service
func ProxyToWager(cfg *config.Config) gin.HandlerFunc {
	targetURL, _ := url.Parse(cfg.WagerServiceURL)
	proxy := httputil.NewSingleHostReverseProxy(targetURL)

	// Custom error handler
	proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
		// Capture error in Sentry
		hub := sentry.GetHubFromContext(r.Context())
		if hub != nil {
			hub.CaptureException(err)
		}
		
		// Return error response
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadGateway)
		fmt.Fprintf(w, `{"error": "Wager service unavailable: %s"}`, err.Error())
	}

	// Modify request before sending
	proxy.Director = func(req *http.Request) {
		req.URL.Scheme = targetURL.Scheme
		req.URL.Host = targetURL.Host
		// Replace /api/v1 with /api for wager service routes
		if strings.HasPrefix(req.URL.Path, "/api/v1/") {
			req.URL.Path = "/api" + strings.TrimPrefix(req.URL.Path, "/api/v1")
		} else {
			req.URL.Path = targetURL.Path + req.URL.Path
		}
		req.Host = targetURL.Host

		// Add trace headers for distributed tracing
		if hub := sentry.GetHubFromContext(req.Context()); hub != nil {
			if span := sentry.TransactionFromContext(req.Context()); span != nil {
				req.Header.Set("sentry-trace", span.ToSentryTrace())
				if baggage := span.ToBaggage(); baggage != "" {
					req.Header.Set("baggage", baggage)
				}
			}
		}
		
		// Add custom headers
		req.Header.Set("X-Forwarded-By", "api-gateway")
		req.Header.Set("X-Original-Host", req.Host)
	}

	return func(c *gin.Context) {
		// Create transaction for this proxy request
		span := sentry.StartSpan(c.Request.Context(), "http.proxy", sentry.WithTransactionName("Proxy to Wager Service"))
		defer span.Finish()
		
		// Add transaction data
		span.SetTag("proxy.target", "wager-service")
		span.SetTag("http.method", c.Request.Method)
		span.SetTag("http.path", c.Request.URL.Path)
		
		// Update context with span
		c.Request = c.Request.WithContext(span.Context())
		
		// Proxy the request
		proxy.ServeHTTP(c.Writer, c.Request)
	}
}