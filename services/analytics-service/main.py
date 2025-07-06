import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import sys
import psutil
import asyncio
import threading
import gc

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.pymongo import PyMongoIntegration
from rabbitmq_consumer import AnalyticsConsumer

from metrics import BusinessMetrics, MetricAnomalyDetector


# УДАЛЕНО - FastAPI автоматически обрабатывает trace propagation
# Не нужно вручную проверять и создавать транзакции

logging.basicConfig(level=logging.INFO)

# Get version from environment or use default
version = os.environ.get('APP_VERSION', '1.0.0')

# Initialize Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
        PyMongoIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    profiles_sample_rate=1.0,
    environment="development",
    debug=True,
    release=f"analytics-service@{version}",
    # Enable session tracking for crash free rate
    auto_session_tracking=True
)

# MongoDB connection
mongo_url = os.environ.get('MONGODB_URL', 'mongodb://admin:password@localhost:27017')
mongo_client = MongoClient(mongo_url)
db = mongo_client.sentry_poc

# RabbitMQ consumer instance
consumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global consumer
    print("Starting Analytics Service lifespan...")
    try:
        consumer = AnalyticsConsumer(db)
        consumer.start()
        print("Analytics consumer started successfully")
        logging.info("Analytics consumer started")
    except Exception as e:
        print(f"Error starting consumer: {e}")
        logging.error(f"Failed to start consumer: {e}")
    yield
    # Shutdown
    if consumer:
        consumer.stop()
    mongo_client.close()
    logging.info("Analytics service shutdown complete")

# FastAPI app
app = FastAPI(title="Analytics Service", version="1.0.0", lifespan=lifespan)

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
    return {"status": "ok", "service": "analytics", "consumer": "running" if consumer else "stopped"}

@app.get("/api/v1/analytics/daily-stats")
async def get_daily_stats(days: int = 7):
    """
    Get daily statistics with intentionally slow aggregation.
    This endpoint demonstrates performance issues with MongoDB aggregation.
    """
    # FastAPI integration автоматически создает и управляет транзакциями
    # Мы просто работаем с spans
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
    # FastAPI автоматически обрабатывает traces
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

@app.get("/api/v1/analytics/realtime/summary")
async def get_realtime_summary():
    """
    Get real-time analytics summary from pre-aggregated data.
    This data is updated by the RabbitMQ consumer.
    """
    # FastAPI автоматически обрабатывает traces
    try:
        # Get today's stats
        today = datetime.now().date().isoformat()
        
        # Fetch pre-aggregated daily stats
        daily_stats = db.daily_stats.find_one({"date": today}) or {}
        payment_stats = db.daily_payments.find_one({"date": today}) or {}
        
        # Get active players count (played in last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        active_players = db.player_stats.count_documents({
            "last_played": {"$gte": one_hour_ago}
        })
        
        # Calculate unique players for today
        unique_players = len(daily_stats.get("unique_players", []))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "today": {
                "total_games": daily_stats.get("total_games", 0),
                "total_bets": daily_stats.get("total_bets", 0),
                "total_payouts": daily_stats.get("total_payouts", 0),
                "total_wins": daily_stats.get("total_wins", 0),
                "win_rate": (daily_stats.get("total_wins", 0) / daily_stats.get("total_games", 1) * 100) if daily_stats.get("total_games", 0) > 0 else 0,
                "unique_players": unique_players,
                "active_players_1h": active_players
            },
            "payments": {
                "total_credits": payment_stats.get("total_credits", 0),
                "credit_amount": payment_stats.get("credit_amount", 0),
                "total_debits": payment_stats.get("total_debits", 0),
                "debit_amount": payment_stats.get("debit_amount", 0),
                "net_revenue": payment_stats.get("debit_amount", 0) - payment_stats.get("credit_amount", 0)
            },
            "data_source": "realtime_consumer"
        }
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/business-metrics/rtp")
async def get_rtp_metrics(hours: int = 24):
    """
    Get RTP (Return to Player) metrics over specified time period.
    """
    # FastAPI автоматически обрабатывает traces
    sentry_sdk.set_tag("transaction.business", "true")
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Calculate RTP from games collection
        with sentry_sdk.start_span(op="db.aggregate", description="Calculate RTP metrics") as span:
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": cutoff_time.timestamp()}
                    }
                },
                {
                    "$facet": {
                        # Overall RTP
                        "overall": [
                            {
                                "$group": {
                                    "_id": None,
                                    "total_bets": {"$sum": "$bet"},
                                    "total_payouts": {"$sum": "$payout"},
                                    "game_count": {"$sum": 1}
                                }
                            }
                        ],
                        # RTP by hour
                        "hourly": [
                            {
                                "$group": {
                                    "_id": {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d %H:00",
                                            "date": {"$toDate": {"$multiply": ["$timestamp", 1000]}}
                                        }
                                    },
                                    "total_bets": {"$sum": "$bet"},
                                    "total_payouts": {"$sum": "$payout"},
                                    "game_count": {"$sum": 1}
                                }
                            },
                            {"$sort": {"_id": -1}}
                        ],
                        # RTP by player
                        "by_player": [
                            {
                                "$group": {
                                    "_id": "$user_id",
                                    "total_bets": {"$sum": "$bet"},
                                    "total_payouts": {"$sum": "$payout"},
                                    "game_count": {"$sum": 1}
                                }
                            },
                            {
                                "$project": {
                                    "user_id": "$_id",
                                    "total_bets": 1,
                                    "total_payouts": 1,
                                    "game_count": 1,
                                    "rtp": {
                                        "$cond": [
                                            {"$gt": ["$total_bets", 0]},
                                            {"$multiply": [{"$divide": ["$total_payouts", "$total_bets"]}, 100]},
                                            0
                                        ]
                                    }
                                }
                            },
                            {"$sort": {"rtp": -1}},
                            {"$limit": 10}
                        ]
                    }
                }
            ]
            
            result = list(db.games.aggregate(pipeline))
            if not result:
                return {"error": "No data available"}
            
            data = result[0]
            
            # Calculate overall RTP
            overall_data = data["overall"][0] if data["overall"] else None
            overall_rtp = 0
            if overall_data and overall_data["total_bets"] > 0:
                overall_rtp = (overall_data["total_payouts"] / overall_data["total_bets"]) * 100
                
                # Track and check for anomalies
                anomaly_detector = MetricAnomalyDetector()
                anomaly_detector.track_with_anomaly_detection(
                    BusinessMetrics.RTP,
                    overall_rtp,
                    unit="percent",
                    tags={"period": f"{hours}h"}
                )
            
            # Calculate hourly RTP
            hourly_rtp = []
            for hour_data in data["hourly"]:
                if hour_data["total_bets"] > 0:
                    rtp = (hour_data["total_payouts"] / hour_data["total_bets"]) * 100
                    hourly_rtp.append({
                        "hour": hour_data["_id"],
                        "rtp": round(rtp, 2),
                        "total_bets": hour_data["total_bets"],
                        "total_payouts": hour_data["total_payouts"],
                        "game_count": hour_data["game_count"]
                    })
            
            span.set_data("hours_analyzed", len(hourly_rtp))
            span.set_data("overall_rtp", overall_rtp)
            
            return {
                "period_hours": hours,
                "overall_rtp": round(overall_rtp, 2),
                "total_bets": overall_data["total_bets"] if overall_data else 0,
                "total_payouts": overall_data["total_payouts"] if overall_data else 0,
                "total_games": overall_data["game_count"] if overall_data else 0,
                "hourly_breakdown": hourly_rtp,
                "top_players_by_rtp": data["by_player"],
                "rtp_threshold": {
                    "min": 85,
                    "max": 98,
                    "status": "normal" if 85 <= overall_rtp <= 98 else "anomaly"
                }
            }
            
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/business-metrics/active-sessions")
async def get_active_sessions():
    """
    Get active gaming sessions and player engagement metrics.
    """
    # FastAPI автоматически обрабатывает traces
    sentry_sdk.set_tag("transaction.business", "true")
    try:
        # Define session timeout (30 minutes)
        session_timeout = 30 * 60  # 30 minutes in seconds
        cutoff_time = time.time() - session_timeout
        
        with sentry_sdk.start_span(op="db.aggregate", description="Calculate active sessions") as span:
            # Get active players
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": cutoff_time}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "last_game": {"$max": "$timestamp"},
                        "games_in_session": {"$sum": 1},
                        "session_bets": {"$sum": "$bet"},
                        "session_payouts": {"$sum": "$payout"}
                    }
                },
                {
                    "$project": {
                        "user_id": "$_id",
                        "last_game": 1,
                        "games_in_session": 1,
                        "session_bets": 1,
                        "session_payouts": 1,
                        "session_duration": {"$subtract": ["$last_game", cutoff_time]}
                    }
                }
            ]
            
            active_sessions = list(db.games.aggregate(pipeline))
            
            # Track active sessions metric
            session_count = len(active_sessions)
            BusinessMetrics.track_metric(BusinessMetrics.ACTIVE_SESSIONS, session_count, "none")
            
            # Calculate engagement metrics
            total_session_bets = sum(s["session_bets"] for s in active_sessions)
            avg_games_per_session = sum(s["games_in_session"] for s in active_sessions) / session_count if session_count > 0 else 0
            
            # Get session distribution by duration
            duration_buckets = {
                "0-5min": 0,
                "5-15min": 0,
                "15-30min": 0
            }
            
            for session in active_sessions:
                duration_minutes = session["session_duration"] / 60
                if duration_minutes <= 5:
                    duration_buckets["0-5min"] += 1
                elif duration_minutes <= 15:
                    duration_buckets["5-15min"] += 1
                else:
                    duration_buckets["15-30min"] += 1
            
            span.set_data("active_sessions", session_count)
            
            return {
                "active_sessions": session_count,
                "total_active_bets": total_session_bets,
                "avg_games_per_session": round(avg_games_per_session, 1),
                "session_duration_distribution": duration_buckets,
                "sessions_detail": [
                    {
                        "user_id": s["user_id"],
                        "games_played": s["games_in_session"],
                        "total_bet": s["session_bets"],
                        "total_payout": s["session_payouts"],
                        "session_profit": s["session_bets"] - s["session_payouts"],
                        "duration_minutes": round(s["session_duration"] / 60, 1)
                    }
                    for s in sorted(active_sessions, key=lambda x: x["session_bets"], reverse=True)[:10]
                ]
            }
                
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/business-metrics/financial-summary")
async def get_financial_summary(days: int = 7):
    """
    Get financial summary including revenue, deposits, withdrawals.
    """
    # FastAPI автоматически обрабатывает traces
    sentry_sdk.set_tag("transaction.business", "true")
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sentry_sdk.start_span(op="db.aggregate", description="Calculate financial metrics") as span:
            # Get transaction summary
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": cutoff_date}
                    }
                },
                {
                    "$facet": {
                        # Daily breakdown
                        "daily": [
                            {
                                "$group": {
                                    "_id": {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$timestamp"
                                        }
                                    },
                                    "total_bets": {"$sum": "$bet"},
                                    "total_payouts": {"$sum": "$payout"},
                                    "transactions": {"$sum": 1},
                                    "unique_players": {"$addToSet": "$user_id"}
                                }
                            },
                            {
                                "$project": {
                                    "date": "$_id",
                                    "total_bets": 1,
                                    "total_payouts": 1,
                                    "net_revenue": {"$subtract": ["$total_bets", "$total_payouts"]},
                                    "transactions": 1,
                                    "unique_players": {"$size": "$unique_players"},
                                    "house_edge": {
                                        "$cond": [
                                            {"$gt": ["$total_bets", 0]},
                                            {"$multiply": [
                                                {"$divide": [
                                                    {"$subtract": ["$total_bets", "$total_payouts"]},
                                                    "$total_bets"
                                                ]},
                                                100
                                            ]},
                                            0
                                        ]
                                    }
                                }
                            },
                            {"$sort": {"date": -1}}
                        ],
                        # Overall summary
                        "summary": [
                            {
                                "$group": {
                                    "_id": None,
                                    "total_bets": {"$sum": "$bet"},
                                    "total_payouts": {"$sum": "$payout"},
                                    "total_transactions": {"$sum": 1},
                                    "wins": {"$sum": {"$cond": ["$win", 1, 0]}},
                                    "losses": {"$sum": {"$cond": ["$win", 0, 1]}}
                                }
                            }
                        ]
                    }
                }
            ]
            
            result = list(db.transactions.aggregate(pipeline))
            if not result:
                return {"error": "No transaction data available"}
            
            data = result[0]
            summary = data["summary"][0] if data["summary"] else {}
            
            # Calculate key metrics
            total_revenue = summary.get("total_bets", 0) - summary.get("total_payouts", 0)
            win_rate = (summary.get("wins", 0) / summary.get("total_transactions", 1)) * 100 if summary.get("total_transactions", 0) > 0 else 0
            
            # Track revenue metric
            BusinessMetrics.track_metric(BusinessMetrics.REVENUE_NET, total_revenue, "currency")
            
            # Check for revenue anomalies
            if total_revenue < 0:
                sentry_sdk.capture_message(
                    f"Negative revenue detected over {days} days: ${total_revenue}",
                    level="warning"
                )
            
            span.set_data("days_analyzed", days)
            span.set_data("total_revenue", total_revenue)
            
            return {
                "period_days": days,
                "summary": {
                    "total_revenue": round(total_revenue, 2),
                    "total_bets": summary.get("total_bets", 0),
                    "total_payouts": summary.get("total_payouts", 0),
                    "total_transactions": summary.get("total_transactions", 0),
                    "win_rate": round(win_rate, 2),
                    "average_bet": round(summary.get("total_bets", 0) / summary.get("total_transactions", 1), 2) if summary.get("total_transactions", 0) > 0 else 0
                },
                "daily_breakdown": data["daily"],
                "revenue_health": {
                    "status": "healthy" if total_revenue > 0 else "warning",
                    "message": "Revenue positive" if total_revenue > 0 else "Revenue negative - investigation required"
                }
            }
                
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/player-details-n1")
async def get_player_details_n1():
    """
    Intentional N+1 query pattern for demonstrating performance issues.
    This endpoint fetches player details in the worst possible way.
    """
    # FastAPI автоматически обрабатывает traces - просто добавляем метаданные
    sentry_sdk.set_tag("antipattern", "n+1_query")
    
    try:
        # First query: Get all active player IDs
        with sentry_sdk.start_span(op="db.query", description="SELECT DISTINCT user_id FROM games WHERE timestamp > ?") as span:
            span.set_data("db.system", "mongodb")
            span.set_data("db.name", "sentry_poc")
            span.set_data("db.collection", "games")
            span.set_data("db.operation", "distinct")
            
            # Get players who played in the last hour
            one_hour_ago = time.time() - 3600
            player_ids = db.games.distinct("user_id", {"timestamp": {"$gte": one_hour_ago}})
            
            # Limit to 20 players for demo
            player_ids = player_ids[:20]
            
            span.set_data("rows_affected", len(player_ids))
            time.sleep(0.05)  # Simulate query time
        
        # N+1 PROBLEM: Fetch details for each player individually
        player_details = []
        
        for i, player_id in enumerate(player_ids):
            # Query 1: Get player's total games
            with sentry_sdk.start_span(op="db.query", description=f"SELECT COUNT(*) FROM games WHERE user_id = '{player_id}'") as span:
                span.set_data("db.system", "mongodb")
                span.set_data("db.name", "sentry_poc")
                span.set_data("db.collection", "games")
                span.set_data("db.operation", "count")
                span.set_data("n_plus_one.index", i)
                
                game_count = db.games.count_documents({"user_id": player_id})
                time.sleep(0.02)  # Simulate query time
            
            # Query 2: Get player's total bets
            with sentry_sdk.start_span(op="db.query", description=f"SELECT SUM(bet) FROM games WHERE user_id = '{player_id}'") as span:
                span.set_data("db.system", "mongodb")
                span.set_data("db.name", "sentry_poc")
                span.set_data("db.collection", "games")
                span.set_data("db.operation", "aggregate")
                span.set_data("n_plus_one.index", i)
                
                bet_result = list(db.games.aggregate([
                    {"$match": {"user_id": player_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$bet"}}}
                ]))
                total_bets = bet_result[0]["total"] if bet_result else 0
                time.sleep(0.02)
            
            # Query 3: Get player's total payouts
            with sentry_sdk.start_span(op="db.query", description=f"SELECT SUM(payout) FROM games WHERE user_id = '{player_id}'") as span:
                span.set_data("db.system", "mongodb")
                span.set_data("db.name", "sentry_poc")
                span.set_data("db.collection", "games")
                span.set_data("db.operation", "aggregate")
                span.set_data("n_plus_one.index", i)
                
                payout_result = list(db.games.aggregate([
                    {"$match": {"user_id": player_id}},
                    {"$group": {"_id": None, "total": {"$sum": "$payout"}}}
                ]))
                total_payouts = payout_result[0]["total"] if payout_result else 0
                time.sleep(0.02)
            
            # Query 4: Get player's last game time
            with sentry_sdk.start_span(op="db.query", description=f"SELECT MAX(timestamp) FROM games WHERE user_id = '{player_id}'") as span:
                span.set_data("db.system", "mongodb")
                span.set_data("db.name", "sentry_poc")
                span.set_data("db.collection", "games")
                span.set_data("db.operation", "find_one")
                span.set_data("n_plus_one.index", i)
                
                last_game = db.games.find_one(
                    {"user_id": player_id},
                    sort=[("timestamp", -1)]
                )
                last_played = last_game["timestamp"] if last_game else None
                time.sleep(0.02)
            
            player_details.append({
                "user_id": player_id,
                "total_games": game_count,
                "total_bets": total_bets,
                "total_payouts": total_payouts,
                "net_profit": total_payouts - total_bets,
                "last_played": last_played
            })
        
        # Add performance issue metadata
        total_queries = 1 + (len(player_ids) * 4)  # 1 initial + 4 per player
        sentry_sdk.set_measurement("db.n_plus_one.count", len(player_ids))
        sentry_sdk.set_measurement("db.n_plus_one.total_queries", total_queries)
        sentry_sdk.set_tag("performance.issue", "n+1_queries")
        
        return {
            "player_count": len(player_details),
            "players": player_details,
            "performance_warning": f"This endpoint executed {total_queries} queries (N+1 pattern). Should use 1 aggregation query instead.",
            "query_pattern": "N+1",
            "queries_executed": {
                "initial_query": 1,
                "per_player_queries": 4,
                "total": total_queries
            }
        }
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/business-metrics/sessions")
async def get_session_metrics():
    """
    Simplified session metrics endpoint for frontend dashboard.
    """
    try:
        # Get active sessions from the active-sessions endpoint data
        thirty_minutes_ago = time.time() - (30 * 60)
        
        # Count unique active users
        active_users = db.games.distinct(
            "user_id",
            {"timestamp": {"$gte": thirty_minutes_ago}}
        )
        
        # Calculate average session duration
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": thirty_minutes_ago}
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "first_game": {"$min": "$timestamp"},
                    "last_game": {"$max": "$timestamp"},
                    "game_count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "game_count": {"$gt": 1}
                }
            },
            {
                "$project": {
                    "duration": {"$subtract": ["$last_game", "$first_game"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_duration": {"$avg": "$duration"}
                }
            }
        ]
        
        duration_result = list(db.games.aggregate(pipeline))
        avg_duration = duration_result[0]["avg_duration"] if duration_result else 300  # Default 5 minutes
        
        return {
            "active_sessions": len(active_users),
            "avg_duration": avg_duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error in session metrics: {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/business-metrics/financial")
async def get_financial_metrics(hours: int = 24):
    """
    Simplified financial metrics for frontend dashboard.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get payment transactions
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": cutoff_time}
                }
            },
            {
                "$facet": {
                    "deposits": [
                        {"$match": {"type": "credit"}},
                        {
                            "$group": {
                                "_id": None,
                                "count": {"$sum": 1},
                                "total": {"$sum": "$amount"},
                                "avg": {"$avg": "$amount"}
                            }
                        }
                    ],
                    "withdrawals": [
                        {"$match": {"type": "debit"}},
                        {
                            "$group": {
                                "_id": None,
                                "count": {"$sum": 1},
                                "total": {"$sum": "$amount"},
                                "avg": {"$avg": "$amount"}
                            }
                        }
                    ]
                }
            }
        ]
        
        result = list(db.transactions.aggregate(pipeline))
        
        deposits = result[0]["deposits"][0] if result and result[0]["deposits"] else {"count": 0, "total": 0, "avg": 0}
        withdrawals = result[0]["withdrawals"][0] if result and result[0]["withdrawals"] else {"count": 0, "total": 0, "avg": 0}
        
        return {
            "period_hours": hours,
            "total_revenue": deposits.get("total", 0) - withdrawals.get("total", 0),
            "deposit_count": deposits.get("count", 0),
            "avg_deposit": deposits.get("avg", 0),
            "withdrawal_count": withdrawals.get("count", 0),
            "avg_withdrawal": withdrawals.get("avg", 0),
            "total_deposits": deposits.get("total", 0),
            "total_withdrawals": withdrawals.get("total", 0)
        }
        
    except Exception as e:
        print(f"Error in financial metrics: {str(e)}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

# Debug endpoints for crash demonstrations
@app.get("/api/debug/crash")
async def debug_crash():
    """Trigger an unhandled exception for Sentry demo"""
    # Add breadcrumbs
    sentry_sdk.add_breadcrumb(
        message="User accessed debug crash endpoint",
        category="debug",
        level="info",
        data={
            "endpoint": "/api/debug/crash",
            "service": "analytics-service"
        }
    )
    
    # Set user context
    sentry_sdk.set_user({
        "id": "debug-analytics-user",
        "username": "analytics_tester"
    })
    
    # Add runtime context
    process = psutil.Process()
    sentry_sdk.set_context("runtime", {
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(interval=0.1),
        "threads": process.num_threads(),
        "python_version": sys.version,
        "fastapi_version": FastAPI.__version__ if hasattr(FastAPI, '__version__') else "unknown"
    })
    
    # Trigger crash
    raise RuntimeError("[DEMO] Analytics Service crash triggered! This demonstrates FastAPI error tracking with rich context.")

@app.get("/api/debug/validation-error")
async def debug_validation_error():
    """Trigger a Pydantic validation error"""
    
    class StrictModel(BaseModel):
        user_id: str
        age: int
        email: str
        
    # Add breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Attempting to validate invalid data",
        category="debug.validation",
        level="warning",
        data={
            "model": "StrictModel",
            "invalid_data": {"user_id": 123, "age": "not_a_number", "email": "invalid"}
        }
    )
    
    # This will raise ValidationError
    try:
        model = StrictModel(user_id=123, age="not_a_number", email="invalid")
    except ValidationError as e:
        # Add context before re-raising
        sentry_sdk.set_context("validation_error", {
            "errors": e.errors(),
            "error_count": e.error_count()
        })
        raise

@app.get("/api/debug/database-error")
async def debug_database_error():
    """Trigger various MongoDB errors"""
    # Add breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Starting database error simulation",
        category="debug.database",
        level="error"
    )
    
    try:
        # Try invalid aggregation pipeline
        with sentry_sdk.start_span(op="db.aggregate", description="Invalid aggregation") as span:
            span.set_data("db.system", "mongodb")
            span.set_data("error.type", "invalid_pipeline")
            
            # This will fail - $invalidOperator doesn't exist
            result = list(db.games.aggregate([
                {"$match": {"user_id": "test"}},
                {"$invalidOperator": {"field": "value"}}
            ]))
            
    except Exception as e:
        # Add database context
        sentry_sdk.set_context("database_error", {
            "operation": "aggregation",
            "pipeline_stage": "$invalidOperator",
            "collection": "games"
        })
        raise

@app.get("/api/debug/timeout")
async def debug_timeout():
    """Simulate a request timeout"""
    # Add breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Starting timeout simulation",
        category="debug.timeout",
        level="warning",
        data={"timeout_seconds": 5}
    )
    
    # Set context
    sentry_sdk.set_context("timeout_context", {
        "intended_duration": 10,
        "timeout_after": 5,
        "operation": "long_running_analysis"
    })
    
    try:
        # This will timeout
        await asyncio.wait_for(
            asyncio.sleep(10),  # Try to sleep for 10 seconds
            timeout=5.0  # But timeout after 5
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Analytics operation timed out after 5 seconds"
        )

@app.get("/api/debug/memory-spike")
async def debug_memory_spike():
    """Create a memory spike to demonstrate memory profiling"""
    # Get initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    # Add breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Creating memory spike",
        category="debug.memory",
        level="warning",
        data={"initial_memory_mb": initial_memory}
    )
    
    # Create large data structures
    large_data = []
    for i in range(5):
        # Create 10MB of data each iteration
        data = 'X' * (10 * 1024 * 1024)
        large_data.append(data)
        
        # Also create some complex objects
        complex_data = {
            f"key_{j}": [k for k in range(1000)]
            for j in range(1000)
        }
        large_data.append(complex_data)
    
    # Get final memory
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    # Log the spike
    sentry_sdk.set_context("memory_spike", {
        "initial_memory_mb": initial_memory,
        "final_memory_mb": final_memory,
        "increase_mb": memory_increase,
        "allocated_chunks": len(large_data)
    })
    
    # Clean up
    del large_data
    gc.collect()
    
    # Capture a message
    sentry_sdk.capture_message(
        f"Memory spike demo: {memory_increase:.2f}MB increase",
        level="warning"
    )
    
    return {
        "status": "Memory spike created and cleaned",
        "memory_increase_mb": memory_increase,
        "final_memory_mb": final_memory
    }

@app.get("/api/debug/slow-query")
async def debug_slow_query():
    """Demonstrate a slow database query"""
    # Add breadcrumb
    sentry_sdk.add_breadcrumb(
        message="Executing intentionally slow query",
        category="debug.performance",
        level="info"
    )
    
    with sentry_sdk.start_span(op="db.aggregate", description="Slow aggregation query") as span:
        span.set_data("db.system", "mongodb")
        span.set_tag("performance.issue", "slow_query")
        
        # Complex aggregation without indexes
        pipeline = [
            # Full collection scan
            {"$match": {"timestamp": {"$exists": True}}},
            
            # Expensive computation
            {
                "$addFields": {
                    "computed_value": {
                        "$multiply": [
                            {"$sin": "$bet"},
                            {"$cos": "$payout"},
                            {"$log": ["$bet", 10]}
                        ]
                    }
                }
            },
            
            # Multiple lookups (simulated joins)
            {
                "$lookup": {
                    "from": "games",
                    "let": {"userId": "$user_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$user_id", "$$userId"]}}},
                        {"$limit": 100}
                    ],
                    "as": "user_history"
                }
            },
            
            # Unwind the array (creates many documents)
            {"$unwind": "$user_history"},
            
            # Group back with calculations
            {
                "$group": {
                    "_id": "$user_id",
                    "total": {"$sum": "$computed_value"},
                    "count": {"$sum": 1},
                    "avg": {"$avg": "$computed_value"}
                }
            },
            
            # Sort without index
            {"$sort": {"total": -1}},
            
            {"$limit": 10}
        ]
        
        start_time = time.time()
        result = list(db.games.aggregate(pipeline, allowDiskUse=True))
        duration = time.time() - start_time
        
        span.set_data("query_duration_seconds", duration)
        span.set_data("result_count", len(result))
        
        return {
            "status": "Slow query completed",
            "duration_seconds": duration,
            "result_count": len(result),
            "performance_impact": "This query performed a full collection scan with complex computations"
        }

# Error handler for unhandled exceptions
@app.exception_handler(Exception)
async def custom_exception_handler(request, exc):
    """Enhanced exception handler with context"""
    # Add request context
    sentry_sdk.set_context("request", {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None
    })
    
    # Capture the exception
    sentry_sdk.capture_exception(exc)
    
    # Return error response
    return {"error": str(exc), "type": type(exc).__name__}, 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)