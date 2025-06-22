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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Sentry
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[TornadoIntegration()],
    traces_sample_rate=1.0,
    environment="development",
    debug=True
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
                
                # Add custom measurements
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
        """Normal efficient slot calculation"""
        symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
        result_symbols = [random.choice(symbols) for _ in range(3)]
        
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
    
    def _is_prime(self, n):
        """Inefficient prime check for CPU spike demo"""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def _calculate_slot_result_cpu_intensive(self):
        """CPU-intensive calculation using prime number generation"""
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
            # Use primes for complex calculations
            symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
            result_symbols = []
            
            for prime in primes:
                # More CPU-intensive operations
                heavy_calc = 0
                for i in range(10000):
                    heavy_calc += np.sin(prime * i) * np.cos(prime / (i + 1))
                    heavy_calc += np.log(abs(heavy_calc) + 1)
                
                # Select symbol based on calculation
                symbol_index = int(abs(heavy_calc) % len(symbols))
                result_symbols.append(symbols[symbol_index])
            
            span.set_data("calculation_iterations", len(primes) * 10000)
        
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

def make_app():
    return web.Application([
        (r"/health", HealthHandler),
        (r"/calculate", CalculateHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8082)
    print("Game Engine started on :8082")
    ioloop.IOLoop.current().start()