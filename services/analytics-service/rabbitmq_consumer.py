import os
import json
import logging
import pika
import threading
from typing import Dict, Any
from pymongo import MongoClient
import sentry_sdk
from sentry_sdk import start_transaction, start_span

logger = logging.getLogger(__name__)

class AnalyticsConsumer:
    """Consumer for analytics events from RabbitMQ with Sentry trace propagation"""
    
    def __init__(self, db):
        self.rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://admin:password@localhost:5672')
        self.db = db
        self.connection = None
        self.channel = None
        self.consumer_thread = None
        self.should_stop = False
        
    def start(self):
        """Start the consumer in a background thread"""
        print("Starting RabbitMQ consumer thread...")
        self.consumer_thread = threading.Thread(target=self._run_consumer, daemon=True)
        self.consumer_thread.start()
        print("RabbitMQ consumer thread started")
        logger.info("Analytics consumer started")
        
    def stop(self):
        """Stop the consumer"""
        self.should_stop = True
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
        logger.info("Analytics consumer stopped")
        
    def _run_consumer(self):
        """Run the consumer loop"""
        print("Consumer thread running...")
        while not self.should_stop:
            try:
                print(f"Attempting to connect to RabbitMQ at {self.rabbitmq_url}")
                self._connect_and_consume()
            except Exception as e:
                print(f"Consumer error: {e}")
                logger.error(f"Consumer error: {e}")
                sentry_sdk.capture_exception(e)
                if not self.should_stop:
                    # Wait before reconnecting
                    print("Waiting 5 seconds before reconnecting...")
                    threading.Event().wait(5)
                    
    def _connect_and_consume(self):
        """Connect to RabbitMQ and start consuming"""
        params = pika.URLParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Declare exchanges and queues
        self.channel.exchange_declare(exchange='gaming', exchange_type='topic', durable=True)
        
        # Game results queue
        self.channel.queue_declare(queue='analytics.game_results', durable=True)
        self.channel.queue_bind(exchange='gaming', queue='analytics.game_results', routing_key='game.result')
        
        # Payment events queue
        self.channel.queue_declare(queue='analytics.payments', durable=True)
        self.channel.queue_bind(exchange='gaming', queue='analytics.payments', routing_key='payment.*')
        
        # Set QoS
        self.channel.basic_qos(prefetch_count=10)
        
        # Start consuming
        self.channel.basic_consume(queue='analytics.game_results', on_message_callback=self._handle_game_result)
        self.channel.basic_consume(queue='analytics.payments', on_message_callback=self._handle_payment_event)
        
        logger.info("Started consuming messages")
        self.channel.start_consuming()
        
    def _handle_game_result(self, channel, method, properties, body):
        """Handle game result messages"""
        try:
            message = json.loads(body)
            trace_headers = message.get('trace', {})
            
            # Log trace headers for debugging
            logger.info(f"Received trace headers: {trace_headers}")
            
            # Continue trace from publisher
            # Extract sentry-trace header and baggage
            sentry_trace = trace_headers.get('sentry-trace', '')
            baggage = trace_headers.get('baggage', '')
            
            # Create transaction with proper trace continuation
            transaction = sentry_sdk.continue_trace(
                {"sentry-trace": sentry_trace, "baggage": baggage},
                op="mq.process",
                name="Process game result"
            )
            
            with sentry_sdk.start_transaction(transaction):
                with start_span(op="analytics.process_game", description="Process game result") as span:
                    game_data = message['data']
                    
                    # Update real-time analytics
                    self._update_game_analytics(game_data)
                    
                    span.set_data("user_id", game_data.get('user_id'))
                    span.set_data("bet", game_data.get('bet'))
                    span.set_data("payout", game_data.get('payout'))
                    span.set_tag("analytics.type", "game_result")
                    
                # Acknowledge message
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Processed game result for user {game_data.get('user_id')}")
                
        except Exception as e:
            logger.error(f"Error processing game result: {e}")
            sentry_sdk.capture_exception(e)
            # Reject and requeue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    def _handle_payment_event(self, channel, method, properties, body):
        """Handle payment event messages"""
        try:
            message = json.loads(body)
            trace_headers = message.get('trace', {})
            
            # Continue trace from publisher
            # Extract sentry-trace header and baggage
            sentry_trace = trace_headers.get('sentry-trace', '')
            baggage = trace_headers.get('baggage', '')
            
            # Create transaction with proper trace continuation
            transaction = sentry_sdk.continue_trace(
                {"sentry-trace": sentry_trace, "baggage": baggage},
                op="mq.process",
                name="Process payment event"
            )
            
            with sentry_sdk.start_transaction(transaction):
                with start_span(op="analytics.process_payment", description="Process payment event") as span:
                    payment_data = message['data']
                    event_type = message['type']
                    
                    # Update payment analytics
                    self._update_payment_analytics(payment_data, event_type)
                    
                    span.set_data("user_id", payment_data.get('userId'))
                    span.set_data("amount", payment_data.get('amount'))
                    span.set_data("event_type", event_type)
                    span.set_tag("analytics.type", "payment_event")
                    
                # Acknowledge message
                channel.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Processed payment {event_type} for user {payment_data.get('userId')}")
                
        except Exception as e:
            logger.error(f"Error processing payment event: {e}")
            sentry_sdk.capture_exception(e)
            # Reject and requeue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    def _update_game_analytics(self, game_data: Dict[str, Any]):
        """Update real-time game analytics in MongoDB"""
        with start_span(op="db.update", description="Update game analytics") as span:
            # Update daily stats
            from datetime import datetime, timezone
            
            # Convert timestamp to date
            timestamp = game_data.get('timestamp', 0)
            date = datetime.fromtimestamp(timestamp, tz=timezone.utc).date()
            date_str = date.isoformat()
            
            # Upsert daily stats
            self.db.daily_stats.update_one(
                {"date": date_str},
                {
                    "$inc": {
                        "total_games": 1,
                        "total_bets": game_data.get('bet', 0),
                        "total_payouts": game_data.get('payout', 0),
                        "total_wins": 1 if game_data.get('win') else 0
                    },
                    "$addToSet": {"unique_players": game_data.get('user_id')},
                    "$setOnInsert": {"date": date_str}
                },
                upsert=True
            )
            
            # Update player stats
            self.db.player_stats.update_one(
                {"user_id": game_data.get('user_id')},
                {
                    "$inc": {
                        "total_games": 1,
                        "total_bets": game_data.get('bet', 0),
                        "total_payouts": game_data.get('payout', 0),
                        "total_wins": 1 if game_data.get('win') else 0
                    },
                    "$set": {"last_played": datetime.fromtimestamp(timestamp, tz=timezone.utc)}
                },
                upsert=True
            )
            
            span.set_data("date", date_str)
            span.set_data("user_id", game_data.get('user_id'))
            
    def _update_payment_analytics(self, payment_data: Dict[str, Any], event_type: str):
        """Update real-time payment analytics in MongoDB"""
        with start_span(op="db.update", description="Update payment analytics") as span:
            from datetime import datetime, timezone
            
            # Convert timestamp to date
            timestamp = payment_data.get('timestamp')
            if isinstance(timestamp, str):
                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
            else:
                date = datetime.now(timezone.utc).date()
            date_str = date.isoformat()
            
            # Update daily payment stats
            self.db.daily_payments.update_one(
                {"date": date_str},
                {
                    "$inc": {
                        f"total_{event_type}s": 1,
                        f"{event_type}_amount": payment_data.get('amount', 0)
                    },
                    "$setOnInsert": {"date": date_str}
                },
                upsert=True
            )
            
            span.set_data("date", date_str)
            span.set_data("event_type", event_type)