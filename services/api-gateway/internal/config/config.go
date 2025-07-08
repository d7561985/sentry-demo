package config

import (
	"os"
)

type Config struct {
	SentryDSN        string
	UserServiceURL   string
	GameServiceURL   string
	PaymentServiceURL string
	WagerServiceURL  string
	RedisURL         string
}

func Load() *Config {
	return &Config{
		SentryDSN:         getEnv("SENTRY_DSN", ""),
		UserServiceURL:    getEnv("USER_SERVICE_URL", "http://user-service:8081"),
		GameServiceURL:    getEnv("GAME_SERVICE_URL", "http://game-engine:8082"),
		PaymentServiceURL: getEnv("PAYMENT_SERVICE_URL", "http://payment-service:8083"),
		WagerServiceURL:   getEnv("WAGER_SERVICE_URL", "http://wager-service:8085"),
		RedisURL:          getEnv("REDIS_URL", "localhost:6379"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}