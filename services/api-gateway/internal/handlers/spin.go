package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/sentry-poc/api-gateway/internal/config"
)

type SpinRequest struct {
	UserID string  `json:"userId" binding:"required"`
	Bet    float64 `json:"bet" binding:"required,min=1,max=1000"`
}

// sentryRoundTripper adds Sentry trace headers to outgoing HTTP requests
type sentryRoundTripper struct {
	transport http.RoundTripper
}

func (s *sentryRoundTripper) RoundTrip(req *http.Request) (*http.Response, error) {
	// Get span from request context
	span := sentry.SpanFromContext(req.Context())
	if span != nil {
		// Add trace headers
		req.Header.Set("sentry-trace", span.ToSentryTrace())
		
		// Get baggage from the transaction
		if transaction := sentry.TransactionFromContext(req.Context()); transaction != nil {
			if baggage := transaction.ToBaggage(); baggage != "" {
				req.Header.Set("baggage", baggage)
			}
		}
	}
	
	// Use default transport if none provided
	transport := s.transport
	if transport == nil {
		transport = http.DefaultTransport
	}
	
	return transport.RoundTrip(req)
}

func Spin(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		// The sentrygin middleware automatically creates a transaction from incoming headers
		// We just need to work with the existing transaction/span
		ctx := c.Request.Context()
		
		// Get the current span from context (created by sentrygin middleware)
		span := sentry.TransactionFromContext(ctx)
		if span != nil {
			// Update the transaction name to be more specific
			span.Name = "POST /api/v1/spin"
			span.SetTag("user.authenticated", "true")
		}

		// Validate request
		var req SpinRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": "Invalid request"})
			return
		}

		// Add user context
		sentry.ConfigureScope(func(scope *sentry.Scope) {
			scope.SetUser(sentry.User{
				ID:       req.UserID,
				Username: fmt.Sprintf("player_%s", req.UserID),
			})
			scope.SetContext("bet", map[string]interface{}{
				"amount": req.Bet,
			})
		})

		// Create HTTP client with Sentry transport
		client := &http.Client{
			Timeout:   10 * time.Second,
			Transport: &sentryRoundTripper{},
		}

		// Forward to game engine
		gameSpan := sentry.StartSpan(ctx, "http.client", sentry.WithDescription("POST game-engine:/spin"))
		gameCtx := gameSpan.Context()
		defer gameSpan.Finish()

		gameReq := map[string]interface{}{
			"userId": req.UserID,
			"bet":    req.Bet,
		}

		body, _ := json.Marshal(gameReq)
		httpReq, err := http.NewRequestWithContext(gameCtx, "POST", "http://game-engine:8082/calculate", bytes.NewBuffer(body))
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to create request"})
			return
		}

		httpReq.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(httpReq)
		if err != nil {
			gameSpan.Status = sentry.SpanStatusInternalError
			sentry.CaptureException(err)
			c.JSON(500, gin.H{"error": "Game engine unavailable"})
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != 200 {
			gameSpan.Status = sentry.SpanStatusInternalError
			bodyBytes, _ := io.ReadAll(resp.Body)
			c.JSON(resp.StatusCode, gin.H{"error": string(bodyBytes)})
			return
		}

		// Parse game result
		var gameResult map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&gameResult); err != nil {
			c.JSON(500, gin.H{"error": "Invalid game response"})
			return
		}

		// Extract values for payment processing
		win := gameResult["win"].(bool)
		payout := gameResult["payout"].(float64)

		// Process payment
		paymentSpan := sentry.StartSpan(ctx, "http.client", sentry.WithDescription("POST payment-service:/process"))
		paymentCtx := paymentSpan.Context()
		defer paymentSpan.Finish()

		paymentReq := map[string]interface{}{
			"userId": req.UserID,
			"bet":    req.Bet,
			"payout": payout,
		}

		paymentBody, _ := json.Marshal(paymentReq)
		paymentHttpReq, err := http.NewRequestWithContext(paymentCtx, "POST", "http://payment-service:8083/process", bytes.NewBuffer(paymentBody))
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to create payment request"})
			return
		}

		paymentHttpReq.Header.Set("Content-Type", "application/json")

		paymentResp, err := client.Do(paymentHttpReq)
		if err != nil {
			paymentSpan.Status = sentry.SpanStatusInternalError
			sentry.CaptureException(err)
			c.JSON(500, gin.H{"error": "Payment service unavailable"})
			return
		}
		defer paymentResp.Body.Close()

		if paymentResp.StatusCode != 200 {
			paymentSpan.Status = sentry.SpanStatusInternalError
			bodyBytes, _ := io.ReadAll(paymentResp.Body)
			c.JSON(paymentResp.StatusCode, gin.H{"error": string(bodyBytes)})
			return
		}

		// Get updated balance
		var paymentResult map[string]interface{}
		if err := json.NewDecoder(paymentResp.Body).Decode(&paymentResult); err != nil {
			c.JSON(500, gin.H{"error": "Invalid payment response"})
			return
		}

		// Update game result with new balance
		gameResult["newBalance"] = paymentResult["newBalance"]

		// Add custom tags
		if span != nil {
			span.SetTag("spin.win", fmt.Sprintf("%v", win))
			span.SetTag("spin.bet", fmt.Sprintf("%.2f", req.Bet))
			span.SetTag("spin.payout", fmt.Sprintf("%.2f", payout))
		}

		// Send metrics
		sentry.CaptureMessage(fmt.Sprintf("Spin completed - User: %s, Win: %v, Payout: %.2f", req.UserID, win, payout))

		c.JSON(200, gameResult)
	}
}