package handlers

import (
	"context"
	"fmt"
	"math/rand"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"github.com/sentry-poc/user-service/internal/models"
)

// SeedGameHistory creates sample game history data for demo purposes
func SeedGameHistory(mongoClient *mongo.Client, userID string) error {
	ctx := context.Background()
	collection := mongoClient.Database("sentry_poc").Collection("game_history")
	
	// Check if we already have data for this user
	count, err := collection.CountDocuments(ctx, bson.M{"user_id": userID})
	if err != nil {
		return err
	}
	
	// If we already have some games, don't seed more
	if count > 0 {
		return nil
	}
	
	// Create 25 sample games
	symbols := []string{"🍒", "🍋", "🍊", "🍇", "⭐", "💎"}
	games := make([]interface{}, 25)
	
	for i := 0; i < 25; i++ {
		// Random game result
		betAmount := float64(10 + rand.Intn(40)) // 10-50
		win := rand.Float32() < 0.3 // 30% win rate
		payout := 0.0
		if win {
			payout = betAmount * float64(2 + rand.Intn(8)) // 2x-10x multiplier
		}
		
		// Random symbols
		gameSymbols := make([]string, 3)
		if win {
			// All same for win
			symbol := symbols[rand.Intn(len(symbols))]
			gameSymbols[0] = symbol
			gameSymbols[1] = symbol
			gameSymbols[2] = symbol
		} else {
			// Random for loss
			for j := 0; j < 3; j++ {
				gameSymbols[j] = symbols[rand.Intn(len(symbols))]
			}
		}
		
		game := models.GameHistory{
			ID:        fmt.Sprintf("game_%s_%d", userID, i),
			UserID:    userID,
			GameType:  "slots",
			BetAmount: betAmount,
			Payout:    payout,
			Result:    gameSymbols,
			PlayedAt:  time.Now().Add(-time.Duration(i) * time.Hour),
			SessionID: fmt.Sprintf("session_%d", i/5),
		}
		
		games[i] = game
	}
	
	// Insert all games
	_, err = collection.InsertMany(ctx, games)
	return err
}