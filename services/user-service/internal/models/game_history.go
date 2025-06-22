package models

import (
	"time"
)

// GameHistory represents a single game played by a user
type GameHistory struct {
	ID         string    `bson:"_id"`
	UserID     string    `bson:"user_id"`
	GameType   string    `bson:"game_type"`
	BetAmount  float64   `bson:"bet_amount"`
	Payout     float64   `bson:"payout"`
	Result     []string  `bson:"result"`
	PlayedAt   time.Time `bson:"played_at"`
	SessionID  string    `bson:"session_id"`
}