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
	"github.com/sentry-poc/user-service/internal/db"
	"github.com/sentry-poc/user-service/internal/handlers"
	"github.com/sentry-poc/user-service/internal/middleware"
)

func main() {
	// Initialize Sentry
	err := sentry.Init(sentry.ClientOptions{
		Dsn:              os.Getenv("SENTRY_DSN"),
		EnableTracing:    true,
		TracesSampleRate: 1.0,
		Environment:      "development",
		Debug:            true,
	})
	if err != nil {
		log.Fatalf("sentry.Init: %s", err)
	}
	defer sentry.Flush(2 * time.Second)

	// Connect to MongoDB
	mongoClient, err := db.ConnectMongoDB(os.Getenv("MONGODB_URL"))
	if err != nil {
		log.Fatalf("Failed to connect to MongoDB: %s", err)
	}
	defer mongoClient.Disconnect(context.Background())

	// Connect to Redis
	redisClient := db.ConnectRedis(os.Getenv("REDIS_URL"))
	defer redisClient.Close()

	// Create handlers
	userHandler := handlers.NewUserHandler(mongoClient, redisClient)

	// Create Gin router
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(sentrygin.New(sentrygin.Options{
		Repanic: true,
	}))

	// Routes
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// Apply auth middleware to protected routes
	router.GET("/balance/:userId", middleware.AuthMiddleware(), userHandler.GetBalance)

	// Start server
	srv := &http.Server{
		Addr:    ":8081",
		Handler: router,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	log.Println("User Service started on :8081")

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
