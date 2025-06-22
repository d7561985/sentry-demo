import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
    traces_sample_rate=1.0,
    environment="development",
    debug=True,
)

# MongoDB connection
mongo_url = os.environ.get('MONGODB_URL', 'mongodb://admin:password@localhost:27017')
mongo_client = MongoClient(mongo_url)
db = mongo_client.sentry_poc

# FastAPI app
app = FastAPI(title="Analytics Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "analytics"}

@app.get("/api/v1/analytics/daily-stats")
async def get_daily_stats(days: int = 7):
    """
    Get daily statistics with intentionally slow aggregation.
    This endpoint demonstrates performance issues with MongoDB aggregation.
    """
    with sentry_sdk.start_transaction(op="analytics.daily_stats", name="Get Daily Stats") as transaction:
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # INTENTIONAL PERFORMANCE ISSUE: Missing index on timestamp field
            # This aggregation pipeline will perform a full collection scan
            with sentry_sdk.start_span(op="db.aggregate", description="Daily stats aggregation") as span:
                span.set_data("db.system", "mongodb")
                span.set_data("db.collection", "games")
                span.set_data("db.operation", "aggregate")
                span.set_tag("performance.issue", "missing_index")
                
                # Simulate slow aggregation with inefficient pipeline
                pipeline = [
                    # Stage 1: Match documents (no index on timestamp)
                    {
                        "$match": {
                            "timestamp": {
                                "$gte": start_date.timestamp(),
                                "$lte": end_date.timestamp()
                            }
                        }
                    },
                    # Stage 2: Add computed fields (expensive)
                    {
                        "$addFields": {
                            "day": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d",
                                    "date": {
                                        "$toDate": {"$multiply": ["$timestamp", 1000]}
                                    }
                                }
                            },
                            "profit": {"$subtract": ["$bet", "$payout"]}
                        }
                    },
                    # Stage 3: Group by day
                    {
                        "$group": {
                            "_id": "$day",
                            "total_games": {"$sum": 1},
                            "total_bets": {"$sum": "$bet"},
                            "total_payouts": {"$sum": "$payout"},
                            "total_wins": {
                                "$sum": {"$cond": [{"$eq": ["$win", True]}, 1, 0]}
                            },
                            "unique_players": {"$addToSet": "$user_id"},
                            "avg_bet": {"$avg": "$bet"},
                            "max_payout": {"$max": "$payout"}
                        }
                    },
                    # Stage 4: Calculate additional metrics
                    {
                        "$project": {
                            "date": "$_id",
                            "total_games": 1,
                            "total_bets": 1,
                            "total_payouts": 1,
                            "total_wins": 1,
                            "unique_players": {"$size": "$unique_players"},
                            "avg_bet": 1,
                            "max_payout": 1,
                            "house_edge": {
                                "$multiply": [
                                    {"$divide": [
                                        {"$subtract": ["$total_bets", "$total_payouts"]},
                                        "$total_bets"
                                    ]},
                                    100
                                ]
                            },
                            "win_rate": {
                                "$multiply": [
                                    {"$divide": ["$total_wins", "$total_games"]},
                                    100
                                ]
                            }
                        }
                    },
                    # Stage 5: Sort by date
                    {"$sort": {"date": -1}}
                ]
                
                # Add artificial delay to simulate slow query
                time.sleep(1)  # Simulate network/processing delay
                
                # Execute aggregation
                cursor = db.games.aggregate(pipeline)
                results = list(cursor)
                
                span.set_data("documents_processed", len(results))
                span.set_data("pipeline_stages", len(pipeline))
            
            # Additional slow operation: Calculate running totals
            with sentry_sdk.start_span(op="calculate.running_totals", description="Calculate running totals") as span:
                for i in range(1, len(results)):
                    # Inefficient calculation of running totals
                    results[i]["running_total_bets"] = sum(r["total_bets"] for r in results[:i+1])
                    results[i]["running_total_games"] = sum(r["total_games"] for r in results[:i+1])
                    # Simulate processing time
                    time.sleep(0.1)
                
                span.set_data("calculations_performed", len(results) - 1)
            
            # Set performance metrics
            sentry_sdk.set_measurement("analytics.days_processed", len(results))
            sentry_sdk.set_measurement("analytics.total_games", sum(r["total_games"] for r in results))
            
            return {
                "days_requested": days,
                "days_returned": len(results),
                "stats": results,
                "performance_warning": "This query performs a full collection scan due to missing indexes"
            }
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/player-metrics/{user_id}")
async def get_player_metrics(user_id: str):
    """
    Get detailed metrics for a specific player.
    Another intentionally slow endpoint.
    """
    with sentry_sdk.start_transaction(op="analytics.player_metrics", name="Get Player Metrics") as transaction:
        try:
            # PERFORMANCE ISSUE: Multiple separate queries instead of one aggregation
            with sentry_sdk.start_span(op="db.queries.multiple", description="Multiple player queries") as span:
                
                # Query 1: Get total games
                games_count = db.games.count_documents({"user_id": user_id})
                time.sleep(0.2)  # Simulate slow query
                
                # Query 2: Get total bets
                total_bets_cursor = db.games.aggregate([
                    {"$match": {"user_id": user_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$bet"}}}
                ])
                total_bets_result = list(total_bets_cursor)
                total_bets = total_bets_result[0]["total"] if total_bets_result else 0
                time.sleep(0.2)
                
                # Query 3: Get total payouts
                total_payouts_cursor = db.games.aggregate([
                    {"$match": {"user_id": user_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$payout"}}}
                ])
                total_payouts_result = list(total_payouts_cursor)
                total_payouts = total_payouts_result[0]["total"] if total_payouts_result else 0
                time.sleep(0.2)
                
                # Query 4: Get win count
                wins_count = db.games.count_documents({"user_id": user_id, "win": True})
                time.sleep(0.2)
                
                # Query 5: Get favorite symbols (inefficient)
                symbol_stats = {}
                games = list(db.games.find({"user_id": user_id}, {"symbols": 1}))
                for game in games:
                    for symbol in game.get("symbols", []):
                        symbol_stats[symbol] = symbol_stats.get(symbol, 0) + 1
                
                span.set_data("queries_executed", 5)
                span.set_data("total_query_time", "0.8s+")
            
            return {
                "user_id": user_id,
                "total_games": games_count,
                "total_bets": total_bets,
                "total_payouts": total_payouts,
                "total_wins": wins_count,
                "win_rate": (wins_count / games_count * 100) if games_count > 0 else 0,
                "net_profit": total_payouts - total_bets,
                "favorite_symbols": symbol_stats,
                "performance_note": "This endpoint makes 5 separate queries instead of using aggregation"
            }
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)