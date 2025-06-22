package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"github.com/sentry-poc/user-service/internal/models"
)

type UserHandler struct {
	mongoClient *mongo.Client
	redisClient *redis.Client
}

func NewUserHandler(mongoClient *mongo.Client, redisClient *redis.Client) *UserHandler {
	return &UserHandler{
		mongoClient: mongoClient,
		redisClient: redisClient,
	}
}

func (h *UserHandler) GetBalance(c *gin.Context) {
	// Get current span from Sentry
	span := sentry.TransactionFromContext(c.Request.Context())
	if span == nil {
		span = sentry.StartTransaction(c.Request.Context(), "user.get_balance")
		defer span.Finish()
	}

	userID := c.Param("userId")
	
	// Create a child span for the database query
	dbSpan := span.StartChild("db.query")
	dbSpan.Description = "Find user by ID"
	dbSpan.SetData("db.system", "mongodb")
	dbSpan.SetData("db.name", "sentry_poc")
	dbSpan.SetData("db.collection", "users")
	
	// INTENTIONAL SLOW QUERY for demo
	// Simulate missing index by adding sleep
	time.Sleep(500 * time.Millisecond)
	
	ctx := context.Background()
	collection := h.mongoClient.Database("sentry_poc").Collection("users")
	
	// First, try to find existing user
	var user models.User
	err := collection.FindOne(ctx, bson.M{"_id": userID}).Decode(&user)
	
	if err == mongo.ErrNoDocuments {
		// Create demo user if not exists
		user = models.User{
			ID:        userID,
			Username:  "demo_player",
			Balance:   1000.0, // Starting balance
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		
		_, err = collection.InsertOne(ctx, user)
		if err != nil {
			dbSpan.Status = sentry.SpanStatusInternalError
			dbSpan.Finish()
			sentry.CaptureException(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
			return
		}
	} else if err != nil {
		dbSpan.Status = sentry.SpanStatusInternalError
		dbSpan.Finish()
		sentry.CaptureException(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}
	
	dbSpan.Status = sentry.SpanStatusOK
	dbSpan.Finish()
	
	// Also demonstrate N+1 query problem
	// This is intentionally bad code for demo
	if c.Query("include_history") == "true" {
		n1Span := span.StartChild("db.query.n1")
		n1Span.Description = "Load user game history (N+1)"
		
		// Simulate N+1 by making multiple queries
		gamesCollection := h.mongoClient.Database("sentry_poc").Collection("games")
		for i := 0; i < 10; i++ {
			gameSpan := n1Span.StartChild("db.query.game")
			gameSpan.Description = "Find game record"
			
			// Simulate individual game query
			time.Sleep(50 * time.Millisecond)
			gamesCollection.FindOne(ctx, bson.M{"user_id": userID, "index": i}, options.FindOne())
			
			gameSpan.Finish()
		}
		
		n1Span.Finish()
	}
	
	c.JSON(http.StatusOK, gin.H{
		"userId":  user.ID,
		"balance": user.Balance,
	})
}