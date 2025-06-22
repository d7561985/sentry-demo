import os
import json
import time
import random
import numpy as np
from tornado import web, ioloop
from pymongo import MongoClient
import sentry_sdk
from sentry_sdk.integrations.tornado import TornadoIntegration
from sentry_sdk import start_transaction, start_span

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
                
                # Start span for RNG calculation
                with start_span(op="game.rng", description="Calculate slot result") as span:
                    # INTENTIONAL CPU SPIKE for demo
                    # Simulate inefficient RNG calculation
                    result = self._calculate_slot_result_inefficient()
                    span.set_data("calculation_method", "inefficient")
                
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
                    db.games.insert_one(game_record)
                
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