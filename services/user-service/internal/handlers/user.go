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

// GetHistory demonstrates N+1 query problem for performance monitoring
func (h *UserHandler) GetHistory(c *gin.Context) {
	// Get current span from Sentry
	span := sentry.TransactionFromContext(c.Request.Context())
	if span == nil {
		span = sentry.StartTransaction(c.Request.Context(), "user.get_history")
		defer span.Finish()
	}

	userID := c.Param("userId")
	ctx := context.Background()
	
	// Seed some demo data if needed
	if err := SeedGameHistory(h.mongoClient, userID); err != nil {
		// Log but don't fail - seeding is optional
		sentry.CaptureException(err)
	}
	
	// First, get the user
	userSpan := span.StartChild("db.query.user")
	userSpan.Description = "Find user by ID"
	userSpan.SetData("db.system", "mongodb")
	userSpan.SetData("db.collection", "users")
	
	collection := h.mongoClient.Database("sentry_poc").Collection("users")
	var user models.User
	err := collection.FindOne(ctx, bson.M{"_id": userID}).Decode(&user)
	userSpan.Finish()
	
	if err != nil {
		sentry.CaptureException(err)
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	// INTENTIONAL N+1 QUERY PROBLEM
	// Bad practice: Get all game IDs first, then fetch each game individually
	historySpan := span.StartChild("db.query.history")
	historySpan.Description = "Get user game history (N+1 problem)"
	historySpan.SetData("antipattern", "n+1_query")
	
	// First query: Get game IDs for this user
	gameIDsSpan := historySpan.StartChild("db.query.game_ids")
	gameIDsSpan.Description = "Find game IDs for user"
	
	historyCollection := h.mongoClient.Database("sentry_poc").Collection("game_history")
	cursor, err := historyCollection.Find(ctx, bson.M{"user_id": userID}, options.Find().SetProjection(bson.M{"_id": 1}).SetLimit(20))
	if err != nil {
		gameIDsSpan.Status = sentry.SpanStatusInternalError
		gameIDsSpan.Finish()
		historySpan.Finish()
		sentry.CaptureException(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch history"})
		return
	}
	
	var gameIDs []string
	for cursor.Next(ctx) {
		var result bson.M
		if err := cursor.Decode(&result); err == nil {
			if id, ok := result["_id"].(string); ok {
				gameIDs = append(gameIDs, id)
			}
		}
	}
	cursor.Close(ctx)
	gameIDsSpan.Finish()
	
	// N+1 PROBLEM: Fetch each game individually
	var games []models.GameHistory
	for i, gameID := range gameIDs {
		// Each iteration is a separate database query
		gameSpan := historySpan.StartChild("db.query.single_game")
		gameSpan.Description = "Fetch individual game"
		gameSpan.SetData("game_index", i)
		gameSpan.SetData("game_id", gameID)
		
		// Simulate slow query
		time.Sleep(50 * time.Millisecond)
		
		var game models.GameHistory
		err := historyCollection.FindOne(ctx, bson.M{"_id": gameID}).Decode(&game)
		if err == nil {
			games = append(games, game)
		}
		
		gameSpan.Finish()
	}
	
	historySpan.SetData("total_queries", len(gameIDs)+1)
	historySpan.SetData("games_fetched", len(games))
	historySpan.Finish()
	
	// Calculate stats
	statsSpan := span.StartChild("calculate.stats")
	totalBet := 0.0
	totalPayout := 0.0
	for _, game := range games {
		totalBet += game.BetAmount
		totalPayout += game.Payout
	}
	statsSpan.Finish()
	
	c.JSON(http.StatusOK, gin.H{
		"userId":       user.ID,
		"totalGames":   len(games),
		"totalBet":     totalBet,
		"totalPayout":  totalPayout,
		"games":        games,
		"queryPattern": "N+1 (bad for performance)",
	})
}