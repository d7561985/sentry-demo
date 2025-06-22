package db

import (
	"github.com/go-redis/redis/v8"
)

func ConnectRedis(url string) *redis.Client {
	opt, err := redis.ParseURL("redis://" + url)
	if err != nil {
		panic(err)
	}

	client := redis.NewClient(opt)
	return client
}