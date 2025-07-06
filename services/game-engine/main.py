import os
import json
import time
import random
import logging
import numpy as np
from tornado import web, ioloop
from pymongo import MongoClient
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration
from sentry_sdk import start_transaction, start_span
from rabbitmq_publisher import get_publisher
from metrics import BusinessMetrics, MetricAnomalyDetector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get version from environment or use default
version = os.environ.get('APP_VERSION', '1.0.0')

# Initialize Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[TornadoIntegration()],
    traces_sample_rate=1.0,
    environment="development",
    # Set profile_session_sample_rate to 1.0 to profile 100%
    # of profile sessions.
    profiles_sample_rate=1.0,
    # Set profile_lifecycle to "trace" to automatically
    # run the profiler on when there is an active transaction
    #profile_lifecycle="trace",
    debug=True,
    release=f"game-engine@{version}"
)

# MongoDB connection
mongo_url = os.environ.get('MONGODB_URL', 'mongodb://admin:password@localhost:27017')
mongo_client = MongoClient(mongo_url)
db = mongo_client.sentry_poc

class HealthHandler(web.RequestHandler):
    def get(self):
        self.write({"status": "ok"})

class CalculateHandler(web.RequestHandler):
    async def post(self):
        # Continue the trace from upstream
        sentry_trace = self.request.headers.get("sentry-trace")
        baggage = self.request.headers.get("baggage")
        
        transaction = sentry_sdk.continue_trace({
            "sentry-trace": sentry_trace,
            "baggage": baggage
        }, op="game.calculate", name="calculate_game_result")
        
        with sentry_sdk.start_transaction(transaction):
            try:
                data = json.loads(self.request.body)
                user_id = data.get('userId')
                bet = data.get('bet')
                cpu_intensive = data.get('cpu_intensive', False)
                
                # Start span for RNG calculation
                with start_span(op="game.rng", description="Calculate slot result") as span:
                    if cpu_intensive:
                        # INTENTIONAL CPU SPIKE for demo
                        # Simulate inefficient RNG calculation with prime numbers
                        result = self._calculate_slot_result_cpu_intensive()
                        span.set_data("calculation_method", "cpu_intensive_primes")
                        span.set_tag("performance.issue", "cpu_spike")
                    else:
                        # Normal efficient calculation
                        result = self._calculate_slot_result_normal()
                        span.set_data("calculation_method", "normal")
                
                # Calculate payout
                win = result['win']
                payout = bet * result['multiplier'] if win else 0
                
                # Store game result in MongoDB
                with start_span(op="db.insert", description="Store game result") as span:
                    span.set_data("db.system", "mongodb")
                    span.set_data("db.collection", "games")
                    
                    game_record = {
                        "user_id": user_id,
                        "bet": bet,
                        "win": win,
                        "payout": payout,
                        "symbols": result['symbols'],
                        "timestamp": time.time()
                    }
                    insert_result = db.games.insert_one(game_record)
                    # Add the ID as string for serialization
                    game_record['_id'] = str(insert_result.inserted_id)
                
                # Publish to RabbitMQ for analytics
                with start_span(op="mq.publish", description="Publish game result to RabbitMQ") as mq_span:
                    try:
                        # Get current trace headers for propagation
                        current_span = sentry_sdk.get_current_span()
                        trace_headers = {
                            'sentry-trace': current_span.to_traceparent() if current_span else '',
                            'baggage': sentry_sdk.get_baggage() or ''
                        }
                        logger.info(f"Publishing with trace headers: {trace_headers}")
                        
                        publisher = get_publisher()
                        publisher.publish_game_result(game_record, trace_headers)
                        
                        mq_span.set_data("mq.queue", "analytics.game_results")
                        mq_span.set_data("mq.routing_key", "game.result")
                        mq_span.set_tag("mq.published", "true")
                        
                    except Exception as mq_error:
                        # Don't fail the request if RabbitMQ is down
                        logger.error(f"Failed to publish to RabbitMQ: {mq_error}")
                        mq_span.set_tag("mq.published", "false")
                        mq_span.set_tag("mq.error", str(mq_error))
                
                # Track business metrics
                with start_span(op="metrics.track", description="Track business metrics") as metric_span:
                    # Track bet and payout volumes
                    BusinessMetrics.track_metric(BusinessMetrics.BET_VOLUME, bet, "currency")
                    BusinessMetrics.track_metric(BusinessMetrics.PAYOUT_VOLUME, payout, "currency")
                    
                    # Track win rate (updated per game)
                    BusinessMetrics.track_metric(BusinessMetrics.WIN_RATE, 100.0 if win else 0.0, "percent")
                    
                    # Calculate and track session RTP
                    session_stats = self._get_session_stats(user_id)
                    if session_stats:
                        session_rtp = BusinessMetrics.track_rtp(
                            session_stats['total_bets'],
                            session_stats['total_payouts'],
                            period="session"
                        )
                        metric_span.set_data("session_rtp", session_rtp)
                    
                    # Track with anomaly detection
                    anomaly_detector = MetricAnomalyDetector()
                    
                    # Calculate 24h rolling RTP
                    rolling_stats = self._get_rolling_stats(24)
                    if rolling_stats:
                        rolling_rtp = BusinessMetrics.track_rtp(
                            rolling_stats['total_bets'],
                            rolling_stats['total_payouts'],
                            period="24h"
                        )
                        anomaly_detector.track_with_anomaly_detection(
                            BusinessMetrics.RTP_ROLLING,
                            rolling_rtp,
                            unit="percent",
                            tags={"period": "24h"}
                        )
                
                # Add custom measurements (legacy)
                sentry_sdk.set_measurement("game.bet_amount", bet)
                sentry_sdk.set_measurement("game.payout", payout)
                sentry_sdk.set_tag("game.win", str(win))
                
                response = {
                    "win": win,
                    "payout": payout,
                    "symbols": result['symbols']
                }
                
                self.set_status(200)
                self.write(response)
                
            except Exception as e:
                sentry_sdk.capture_exception(e)
                self.set_status(500)
                self.write({"error": str(e)})
    
    def _calculate_slot_result_normal(self):
        """Normal slot calculation with 90% RTP"""
        symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
        
        # Symbol weights for 90% RTP
        # Higher weight = more frequent appearance
        symbol_weights = {
            '🍒': 30,  # 2x multiplier - most frequent
            '🍋': 25,  # 3x multiplier
            '🍊': 20,  # 4x multiplier
            '🍇': 15,  # 5x multiplier
            '⭐': 8,   # 10x multiplier
            '💎': 2    # 20x multiplier - rarest
        }
        
        # Create weighted symbol list
        weighted_symbols = []
        for symbol, weight in symbol_weights.items():
            weighted_symbols.extend([symbol] * weight)
        
        # 90% RTP calculation:
        # Win probability should be ~30% to achieve 90% RTP with average multiplier of 3x
        # 30% win * 3x average multiplier = 90% RTP
        
        # Determine if this spin wins (30% chance)
        is_winning_spin = random.random() < 0.30
        
        if is_winning_spin:
            # For winning spins, select one symbol for all reels
            winning_symbol = random.choice(weighted_symbols)
            result_symbols = [winning_symbol, winning_symbol, winning_symbol]
            win = True
        else:
            # For losing spins, ensure at least one symbol is different
            result_symbols = [random.choice(weighted_symbols) for _ in range(3)]
            # Force a mismatch if accidentally all match
            if result_symbols[0] == result_symbols[1] == result_symbols[2]:
                # Change the middle symbol
                other_symbols = [s for s in symbols if s != result_symbols[0]]
                result_symbols[1] = random.choice(other_symbols)
            win = False
        
        # Calculate multiplier based on symbol
        multipliers = {
            '🍒': 2,
            '🍋': 3,
            '🍊': 4,
            '🍇': 5,
            '⭐': 10,
            '💎': 20
        }
        
        multiplier = multipliers.get(result_symbols[0], 1) if win else 0
        
        return {
            'symbols': result_symbols,
            'win': win,
            'multiplier': multiplier
        }
    
    def _is_prime(self, n):
        """Inefficient prime check for CPU spike demo"""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def _calculate_slot_result_cpu_intensive(self):
        """CPU-intensive calculation with 90% RTP using prime number generation"""
        with start_span(op="cpu.prime_generation", description="Generate large primes") as span:
            # Generate large prime numbers (VERY inefficient on purpose)
            primes = []
            num = 1000000  # Start with a large number
            while len(primes) < 3:
                if self._is_prime(num):
                    primes.append(num)
                num += 1
            span.set_data("primes_generated", primes)
        
        with start_span(op="cpu.heavy_calculation", description="Heavy math operations") as span:
            # Symbol weights for 90% RTP
            symbol_weights = {
                '🍒': 30,  # 2x multiplier - most frequent
                '🍋': 25,  # 3x multiplier
                '🍊': 20,  # 4x multiplier
                '🍇': 15,  # 5x multiplier
                '⭐': 8,   # 10x multiplier
                '💎': 2    # 20x multiplier - rarest
            }
            
            # Create weighted symbol list
            symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
            weighted_symbols = []
            for symbol, weight in symbol_weights.items():
                weighted_symbols.extend([symbol] * weight)
            
            # Do heavy calculations to determine win (30% chance for 90% RTP)
            heavy_calc_sum = 0
            for prime in primes:
                # CPU-intensive operations
                for i in range(10000):
                    heavy_calc_sum += np.sin(prime * i) * np.cos(prime / (i + 1))
                    heavy_calc_sum += np.log(abs(heavy_calc_sum) + 1)
            
            # Use the heavy calculation to determine if this is a winning spin
            # Normalize to 0-1 range and check if < 0.30 for 30% win rate
            win_threshold = abs(heavy_calc_sum) % 100 / 100.0
            is_winning_spin = win_threshold < 0.30
            
            if is_winning_spin:
                # For winning spins, select one symbol for all reels
                # Use prime-based calculation to select symbol
                symbol_selector = int(abs(heavy_calc_sum * primes[0]) % len(weighted_symbols))
                winning_symbol = weighted_symbols[symbol_selector]
                result_symbols = [winning_symbol, winning_symbol, winning_symbol]
                win = True
            else:
                # For losing spins, use different calculations for each reel
                result_symbols = []
                for i, prime in enumerate(primes):
                    # More CPU work for each symbol
                    reel_calc = 0
                    for j in range(5000):
                        reel_calc += np.sin(prime * j * (i + 1))
                        reel_calc += np.cos(prime / (j + 1))
                    
                    symbol_index = int(abs(reel_calc) % len(weighted_symbols))
                    result_symbols.append(weighted_symbols[symbol_index])
                
                # Ensure at least one symbol is different
                if result_symbols[0] == result_symbols[1] == result_symbols[2]:
                    other_symbols = [s for s in symbols if s != result_symbols[0]]
                    result_symbols[1] = random.choice(other_symbols)
                win = False
            
            span.set_data("calculation_iterations", len(primes) * 15000)
            span.set_data("win_threshold", win_threshold)
        
        # Calculate multiplier based on symbol
        multipliers = {
            '🍒': 2,
            '🍋': 3,
            '🍊': 4,
            '🍇': 5,
            '⭐': 10,
            '💎': 20
        }
        
        multiplier = multipliers.get(result_symbols[0], 1) if win else 0
        
        return {
            'symbols': result_symbols,
            'win': win,
            'multiplier': multiplier
        }
    
    def _get_session_stats(self, user_id: str):
        """Get session statistics for RTP calculation"""
        try:
            # Get games from last hour (session)
            one_hour_ago = time.time() - 3600
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": one_hour_ago}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_bets": {"$sum": "$bet"},
                        "total_payouts": {"$sum": "$payout"},
                        "game_count": {"$sum": 1}
                    }
                }
            ]
            result = list(db.games.aggregate(pipeline))
            if result:
                return result[0]
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
        return None
    
    def _get_rolling_stats(self, hours: int):
        """Get rolling statistics for RTP calculation"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": cutoff_time}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_bets": {"$sum": "$bet"},
                        "total_payouts": {"$sum": "$payout"},
                        "game_count": {"$sum": 1},
                        "unique_players": {"$addToSet": "$user_id"}
                    }
                },
                {
                    "$project": {
                        "total_bets": 1,
                        "total_payouts": 1,
                        "game_count": 1,
                        "unique_player_count": {"$size": "$unique_players"}
                    }
                }
            ]
            result = list(db.games.aggregate(pipeline))
            if result:
                return result[0]
        except Exception as e:
            logger.error(f"Error getting rolling stats: {e}")
        return None
    
    def _calculate_slot_result_inefficient(self):
        """Intentionally inefficient calculation for CPU spike demo"""
        # Simulate complex calculation with nested loops
        # This is BAD code for demonstration purposes
        
        symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
        result_symbols = []
        
        # Inefficient random selection
        for _ in range(3):
            # Simulate heavy computation
            heavy_calc = 0
            for i in range(100000):  # Intentionally high iteration
                heavy_calc += np.random.random() * np.sin(i) * np.cos(i)
            
            # Select symbol
            symbol_index = int(abs(heavy_calc) % len(symbols))
            result_symbols.append(symbols[symbol_index])
        
        # Check if win (all symbols match)
        win = all(s == result_symbols[0] for s in result_symbols)
        
        # Calculate multiplier based on symbol
        multipliers = {
            '🍒': 2,
            '🍋': 3,
            '🍊': 4,
            '🍇': 5,
            '⭐': 10,
            '💎': 20
        }
        
        multiplier = multipliers.get(result_symbols[0], 1) if win else 0
        
        return {
            'symbols': result_symbols,
            'win': win,
            'multiplier': multiplier
        }

class BusinessMetricsHandler(web.RequestHandler):
    """Endpoint to trigger business metric scenarios"""
    async def post(self):
        # Check for incoming trace headers
        sentry_trace = self.request.headers.get('sentry-trace', '')
        baggage = self.request.headers.get('baggage', '')
        
        # Continue trace if headers present, otherwise create new transaction
        if sentry_trace:
            transaction = sentry_sdk.continue_trace({
                "sentry-trace": sentry_trace,
                "baggage": baggage
            }, op="business.demo", name="business_metrics_scenario")
        else:
            transaction = {
                "op": "business.demo",
                "name": "business_metrics_scenario"
            }
        
        with sentry_sdk.start_transaction(transaction):
            try:
                data = json.loads(self.request.body)
                scenario = data.get('scenario', 'normal')
                
                if scenario == 'rtp_anomaly':
                    # Simulate RTP dropping below threshold
                    with start_span(op="demo.rtp_anomaly", description="Simulate RTP anomaly"):
                        anomaly_detector = MetricAnomalyDetector()
                        # Track abnormally low RTP
                        anomaly_detector.track_with_anomaly_detection(
                            BusinessMetrics.RTP,
                            75.0,  # Below 85% threshold
                            unit="percent",
                            tags={"scenario": "demo", "alert": "critical"}
                        )
                        # Also track high RTP
                        anomaly_detector.track_with_anomaly_detection(
                            BusinessMetrics.RTP,
                            99.5,  # Above 98% threshold
                            unit="percent", 
                            tags={"scenario": "demo", "alert": "warning"}
                        )
                    
                    self.write({"status": "RTP anomaly triggered", "low_rtp": 75.0, "high_rtp": 99.5})
                
                elif scenario == 'session_surge':
                    # Simulate sudden increase in active sessions
                    with start_span(op="demo.session_surge", description="Simulate session surge"):
                        # Normal sessions
                        BusinessMetrics.track_metric(BusinessMetrics.ACTIVE_SESSIONS, 150, "none")
                        # Sudden surge
                        BusinessMetrics.track_metric(BusinessMetrics.ACTIVE_SESSIONS, 850, "none", 
                                                   {"surge": "true", "alert": "info"})
                    
                    self.write({"status": "Session surge triggered", "normal": 150, "surge": 850})
                
                elif scenario == 'win_rate_manipulation':
                    # Simulate suspicious win rate patterns
                    with start_span(op="demo.win_rate", description="Simulate win rate manipulation"):
                        anomaly_detector = MetricAnomalyDetector()
                        # Abnormally high win rate
                        anomaly_detector.track_with_anomaly_detection(
                            BusinessMetrics.WIN_RATE,
                            85.0,  # Way above 50% threshold
                            unit="percent",
                            tags={"scenario": "demo", "alert": "critical", "fraud_risk": "high"}
                        )
                    
                    self.write({"status": "Win rate anomaly triggered", "suspicious_rate": 85.0})
                
                else:
                    # Normal metrics
                    with start_span(op="demo.normal", description="Normal business metrics"):
                        BusinessMetrics.track_metric(BusinessMetrics.RTP, 95.5, "percent")
                        BusinessMetrics.track_metric(BusinessMetrics.WIN_RATE, 35.0, "percent")
                        BusinessMetrics.track_metric(BusinessMetrics.ACTIVE_SESSIONS, 250, "none")
                    
                    self.write({"status": "Normal metrics tracked"})
                
                self.set_status(200)
                
            except Exception as e:
                sentry_sdk.capture_exception(e)
                self.set_status(500)
                self.write({"error": str(e)})

def make_app():
    return web.Application([
        (r"/health", HealthHandler),
        (r"/calculate", CalculateHandler),
        (r"/business-metrics", BusinessMetricsHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8082)
    print("Game Engine started on :8082")
    ioloop.IOLoop.current().start()