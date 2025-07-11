package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/getsentry/sentry-go"
	sentrygin "github.com/getsentry/sentry-go/gin"
	"github.com/gin-gonic/gin"
	"github.com/sentry-poc/api-gateway/internal/config"
	"github.com/sentry-poc/api-gateway/internal/handlers"
	"github.com/sentry-poc/api-gateway/internal/middleware"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Get version from environment or use default
	version := os.Getenv("APP_VERSION")
	if version == "" {
		version = "1.0.0"
	}

	// Initialize Sentry
	err := sentry.Init(sentry.ClientOptions{
		Dsn:              cfg.SentryDSN,
		EnableTracing:    true,
		TracesSampleRate: 1.0,
		Environment:      "development",
		Debug:            true,
		Release:          "api-gateway@" + version,
		// IMPORTANT: Attach stack traces to all errors for better debugging
		AttachStacktrace: true,
		// Set sample rate for errors (not just traces)
		SampleRate: 1.0,
		// Maximum breadcrumbs
		MaxBreadcrumbs: 100,
		// BeforeSend hook to enrich errors
		BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
			// Add additional context to all errors
			if event.Exception != nil && len(event.Exception) > 0 {
				event.Fingerprint = []string{"{{ default }}", event.Exception[0].Type}
			}
			return event
		},
	})
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}
	defer sentry.Flush(2 * time.Second)

	// Create Gin router
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(sentrygin.New(sentrygin.Options{
		Repanic: true,
	}))
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// User endpoints
		api.GET("/users/:userId/balance", middleware.Auth(), handlers.GetUserBalance(cfg))
		api.GET("/user/:userId/history", middleware.Auth(), handlers.GetUserHistory(cfg))
		
		// Spin endpoint - main game action
		api.POST("/spin", middleware.Auth(), handlers.Spin(cfg))
		
		// Analytics endpoints - proxy to analytics service
		api.Any("/analytics/*path", handlers.ProxyToAnalytics(cfg))
		api.Any("/business-metrics/*path", handlers.ProxyToAnalytics(cfg))
		
		// Game engine endpoints - proxy to game engine service (including debug)
		api.Any("/game-engine/*path", handlers.ProxyToGameEngine(cfg))
		
		// Payment endpoints - proxy to payment service (including debug)
		api.Any("/payment/*path", handlers.ProxyToPayment(cfg))
		
		// Wager endpoints - proxy to wager service (including bonus endpoints)
		api.Any("/wager/*path", handlers.ProxyToWager(cfg))
		api.Any("/bonus/*path", handlers.ProxyToWager(cfg))
		
		// Trigger panic for demo (Scenario 2)
		api.GET("/debug/panic/:userId", handlers.TriggerPanic())
	}

	// Start server
	srv := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	// Graceful shutdown
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	log.Println("API Gateway started on :8080")

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	log.Println("Server exiting")
}