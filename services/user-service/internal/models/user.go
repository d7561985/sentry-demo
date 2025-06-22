package models

import (
	"time"
)

type User struct {
	ID        string    `bson:"_id"`
	Username  string    `bson:"username"`
	Balance   float64   `bson:"balance"`
	CreatedAt time.Time `bson:"created_at"`
	UpdatedAt time.Time `bson:"updated_at"`
}