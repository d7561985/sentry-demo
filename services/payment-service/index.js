const express = require('express');
const { MongoClient } = require('mongodb');
const Sentry = require('@sentry/node');
const { getPublisher } = require('./rabbitmqPublisher');

const app = express();
const PORT = process.env.PORT || 8083;
const ERROR_RATE = 0.1; // 10% error rate for demo

// Initialize Sentry FIRST
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    Sentry.httpIntegration({ tracing: true }),
    Sentry.expressIntegration({ app }),
  ],
  tracesSampleRate: 1.0,
  environment: 'development',
  debug: true,
});

// Connect to MongoDB
let db;
MongoClient.connect(process.env.MONGODB_URL || 'mongodb://mongodb:27017/sentry-poc', {
  useUnifiedTopology: true
}).then(client => {
  console.log('Connected to MongoDB');
  db = client.db('sentry_poc');
}).catch(err => {
  console.error('Failed to connect to MongoDB:', err);
  process.exit(1);
});

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Process payment endpoint
app.post('/process', async (req, res) => {
  // Continue trace from upstream
  const sentryTraceHeader = req.get('sentry-trace');
  const baggageHeader = req.get('baggage');
  
  // Use continueTrace if we have headers, otherwise just execute
  const handler = async () => {
    try {
    const { userId, bet, payout } = req.body;

    // INTENTIONAL RANDOM FAILURES for demo (10% error rate)
    if (Math.random() < ERROR_RATE) {
      const error = new Error('Payment provider timeout');
      Sentry.captureException(error);
      return res.status(500).json({ error: 'Payment processing failed' });
    }

    // Simulate external payment provider API call
    const delay = await Sentry.startSpan(
      {
        name: 'External payment provider API',
        op: 'http.client',
        attributes: {
          'http.method': 'POST',
          'http.url': 'https://payment-provider.example.com/charge'
        }
      },
      async () => {
        // INTENTIONAL SLOW EXTERNAL API for demo (2-5 seconds)
        const apiDelay = 2000 + Math.random() * 3000;
        await new Promise(resolve => setTimeout(resolve, apiDelay));
        return apiDelay;
      }
    );

    // Update user balance in database
    const result = await Sentry.startSpan(
      {
        name: 'Update user balance',
        op: 'db.update',
        attributes: {
          'db.system': 'mongodb',
          'db.collection': 'users',
          'db.operation': 'findOneAndUpdate'
        }
      },
      async () => {
        const netChange = payout - bet;
        
        // First check if user exists
        const existingUser = await db.collection('users').findOne({ _id: userId });
        
        if (!existingUser) {
          // Create new user with starting balance
          const newUser = {
            _id: userId,
            username: 'demo_player',
            balance: 1000 + netChange, // Starting balance + net change
            created_at: new Date(),
            updated_at: new Date()
          };
          await db.collection('users').insertOne(newUser);
          return { value: newUser };
        } else {
          // Update existing user
          return await db.collection('users').findOneAndUpdate(
            { _id: userId },
            { 
              $inc: { balance: netChange },
              $set: { updated_at: new Date() }
            },
            { returnDocument: 'after' }
          );
        }
      }
    );

    if (!result.value) {
      throw new Error('User not found');
    }

    // Record transaction
    const transaction = await Sentry.startSpan(
      {
        name: 'Record transaction',
        op: 'db.insert',
        attributes: {
          'db.system': 'mongodb',
          'db.collection': 'transactions'
        }
      },
      async () => {
        const netChange = payout - bet;
        const transaction = {
          user_id: userId,
          type: netChange >= 0 ? 'WIN' : 'LOSS',
          amount: Math.abs(netChange),
          bet: bet,
          payout: payout,
          timestamp: new Date(),
          balance_after: result.value.balance
        };
        await db.collection('transactions').insertOne(transaction);
        return transaction;
      }
    );

    // Publish to RabbitMQ for analytics
    try {
      const publisher = getPublisher();
      const traceHeaders = {
        'sentry-trace': Sentry.getActiveSpan()?.toTraceparent() || '',
        'baggage': Sentry.getBaggage() || ''
      };
      
      const netChange = payout - bet;
      await publisher.publishPaymentEvent(
        netChange >= 0 ? 'credit' : 'debit',
        {
          userId,
          amount: Math.abs(netChange),
          bet,
          payout,
          balance_after: result.value.balance,
          timestamp: transaction.timestamp
        },
        traceHeaders
      );
    } catch (mqError) {
      // Don't fail the request if RabbitMQ is down
      console.error('Failed to publish to RabbitMQ:', mqError);
    }

    // Set custom metrics
    const netChange = payout - bet;
    Sentry.metrics.distribution('payment.amount', Math.abs(netChange));
    Sentry.metrics.distribution('payment.processing_time', delay);
    Sentry.getCurrentScope().setTag('payment.type', netChange >= 0 ? 'credit' : 'debit');

    res.json({
      success: true,
      newBalance: result.value.balance
    });

    } catch (error) {
      Sentry.captureException(error);
      res.status(500).json({ error: error.message });
    }
  };

  // Execute with or without trace context
  if (sentryTraceHeader) {
    await Sentry.continueTrace(
      { sentryTrace: sentryTraceHeader, baggage: baggageHeader },
      handler
    );
  } else {
    await handler();
  }
});

// Error handler
Sentry.setupExpressErrorHandler(app);

// Start server
app.listen(PORT, () => {
  console.log(`Payment Service started on :${PORT}`);
});