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
	UserID string  `json:"userId"`
	Bet    float64 `json:"bet"`
}

type SpinResponse struct {
	Win        bool     `json:"win"`
	Payout     float64  `json:"payout"`
	NewBalance float64  `json:"newBalance"`
	Symbols    []string `json:"symbols"`
}

func Spin(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get current span from Sentry
		span := sentry.TransactionFromContext(c.Request.Context())
		if span == nil {
			// Create new transaction if none exists
			span = sentry.StartTransaction(c.Request.Context(), "spin-request", sentry.WithOpName("http.server"))
			defer span.Finish()
		}

		// Parse request
		var req SpinRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request"})
			return
		}

		// Get user ID from context (set by auth middleware)
		userID, _ := c.Get("userId")
		if req.UserID == "" {
			req.UserID = userID.(string)
		}

		// Step 1: Check user balance
		balanceSpan := span.StartChild("user.check_balance")
		balance, err := checkUserBalance(c, cfg.UserServiceURL, req.UserID, balanceSpan)
		balanceSpan.Finish()
		
		if err != nil {
			sentry.CaptureException(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check balance"})
			return
		}

		if balance < req.Bet {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient balance"})
			return
		}

		// Step 2: Calculate game result
		gameSpan := span.StartChild("game.calculate_result")
		gameResult, err := calculateGameResult(c, cfg.GameServiceURL, req.UserID, req.Bet, gameSpan)
		gameSpan.Finish()
		
		if err != nil {
			sentry.CaptureException(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Game engine error"})
			return
		}

		// Step 3: Process payment
		paymentSpan := span.StartChild("payment.process")
		newBalance, err := processPayment(c, cfg.PaymentServiceURL, req.UserID, req.Bet, gameResult.Payout, paymentSpan)
		paymentSpan.Finish()
		
		if err != nil {
			sentry.CaptureException(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Payment processing failed"})
			return
		}

		// Return result
		response := SpinResponse{
			Win:        gameResult.Win,
			Payout:     gameResult.Payout,
			NewBalance: newBalance,
			Symbols:    gameResult.Symbols,
		}

		c.JSON(http.StatusOK, response)
	}
}

func checkUserBalance(c *gin.Context, userServiceURL, userID string, parentSpan *sentry.Span) (float64, error) {
	span := parentSpan.StartChild("http.client")
	span.Description = "GET /balance"
	defer span.Finish()

	url := fmt.Sprintf("%s/balance/%s", userServiceURL, userID)
	
	// Create request with trace headers
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return 0, err
	}

	// Propagate trace context
	req.Header.Set("sentry-trace", span.ToSentryTrace())
	if baggage := c.GetHeader("baggage"); baggage != "" {
		req.Header.Set("baggage", baggage)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		span.Status = sentry.SpanStatusInternalError
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		span.Status = sentry.SpanStatusInternalError
		return 0, fmt.Errorf("user service returned status %d", resp.StatusCode)
	}

	var result struct {
		Balance float64 `json:"balance"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0, err
	}

	span.Status = sentry.SpanStatusOK
	return result.Balance, nil
}

func calculateGameResult(c *gin.Context, gameServiceURL, userID string, bet float64, parentSpan *sentry.Span) (*SpinResponse, error) {
	span := parentSpan.StartChild("http.client")
	span.Description = "POST /calculate"
	defer span.Finish()

	url := fmt.Sprintf("%s/calculate", gameServiceURL)
	payload := map[string]interface{}{
		"userId": userID,
		"bet":    bet,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	// Propagate trace context
	req.Header.Set("sentry-trace", span.ToSentryTrace())
	if baggage := c.GetHeader("baggage"); baggage != "" {
		req.Header.Set("baggage", baggage)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		span.Status = sentry.SpanStatusInternalError
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		span.Status = sentry.SpanStatusInternalError
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("game service error: %s", string(body))
	}

	var result SpinResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	span.Status = sentry.SpanStatusOK
	return &result, nil
}

func processPayment(c *gin.Context, paymentServiceURL, userID string, bet, payout float64, parentSpan *sentry.Span) (float64, error) {
	span := parentSpan.StartChild("http.client")
	span.Description = "POST /process"
	defer span.Finish()

	url := fmt.Sprintf("%s/process", paymentServiceURL)
	payload := map[string]interface{}{
		"userId": userID,
		"bet":    bet,
		"payout": payout,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return 0, err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return 0, err
	}
	req.Header.Set("Content-Type", "application/json")

	// Propagate trace context
	req.Header.Set("sentry-trace", span.ToSentryTrace())
	if baggage := c.GetHeader("baggage"); baggage != "" {
		req.Header.Set("baggage", baggage)
	}

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		span.Status = sentry.SpanStatusInternalError
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		span.Status = sentry.SpanStatusInternalError
		body, _ := io.ReadAll(resp.Body)
		return 0, fmt.Errorf("payment service error: %s", string(body))
	}

	var result struct {
		NewBalance float64 `json:"newBalance"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0, err
	}

	span.Status = sentry.SpanStatusOK
	return result.NewBalance, nil
}