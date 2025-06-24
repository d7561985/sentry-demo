// IMPORTANT: Initialize Sentry BEFORE all other imports
const Sentry = require('./instrument');

const express = require('express');
const { MongoClient } = require('mongodb');
const { getPublisher } = require('./rabbitmqPublisher');
// Import business metrics
const { BusinessMetrics, MetricAnomalyDetector } = require('./metrics.js');

const app = express();
const PORT = process.env.PORT || 8083;
const ERROR_RATE = 0.1; // 10% error rate for demo

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
        const apiDelay = Math.random() * 1000;
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
      const activeSpan = Sentry.getActiveSpan();
      const traceHeaders = {
        'sentry-trace': activeSpan ? Sentry.spanToTraceHeader(activeSpan) : '',
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

    // Track business metrics
    await Sentry.startSpan(
      {
        name: 'Track financial metrics',
        op: 'metrics.track',
      },
      async () => {
        const netChange = payout - bet;
        const anomalyDetector = new MetricAnomalyDetector();
        
        // Track financial volumes
        if (netChange >= 0) {
          // Credit (winnings)
          BusinessMetrics.trackMetric(BusinessMetrics.DEPOSIT_AMOUNT, netChange, "currency");
          BusinessMetrics.trackMetric(BusinessMetrics.DEPOSIT_COUNT, 1, "none");
        } else {
          // Debit (losses)
          BusinessMetrics.trackMetric(BusinessMetrics.WITHDRAWAL_AMOUNT, Math.abs(netChange), "currency");
          BusinessMetrics.trackMetric(BusinessMetrics.WITHDRAWAL_COUNT, 1, "none");
        }
        
        // Track net revenue (house edge)
        const houseEdge = bet - payout;
        BusinessMetrics.trackMetric(BusinessMetrics.REVENUE_NET, houseEdge, "currency");
        
        // Track payment success rate (we're here, so it's successful)
        BusinessMetrics.trackMetric(BusinessMetrics.PAYMENT_SUCCESS_RATE, 100.0, "percent");
        
        // Calculate daily financial metrics
        const dailyStats = await getDailyFinancialStats(db);
        if (dailyStats) {
          // Check for revenue anomalies
          const revenueRate = (dailyStats.totalRevenue / dailyStats.totalBets) * 100;
          if (revenueRate < 0) {
            Sentry.captureMessage(
              `Negative revenue detected: ${revenueRate.toFixed(2)}%`,
              'warning'
            );
          }
        }
      }
    );
    
    // Set custom metrics (legacy)
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

// Financial metrics demo endpoint
app.post('/financial-metrics', async (req, res) => {
  const handler = async () => {
    const transaction = BusinessMetrics.startBusinessTransaction('financial_metrics_demo');
    
    await Sentry.startTransaction(transaction, async () => {
      try {
        const { scenario } = req.body;
        const anomalyDetector = new MetricAnomalyDetector();
        
        if (scenario === 'payment_failure_spike') {
          // Simulate payment failures
          await Sentry.startSpan(
            {
              name: 'Simulate payment failures',
              op: 'demo.payment_failures',
            },
            async () => {
              // Track declining success rate
              anomalyDetector.trackWithAnomalyDetection(
                BusinessMetrics.PAYMENT_SUCCESS_RATE,
                85.0, // Below 95% threshold
                "percent",
                { scenario: "demo", alert: "critical" }
              );
              
              // Track multiple failed transactions
              for (let i = 0; i < 5; i++) {
                Sentry.captureException(new Error(`Payment provider error ${i + 1}`));
              }
            }
          );
          
          res.json({ status: "Payment failure spike triggered", success_rate: 85.0 });
          
        } else if (scenario === 'revenue_anomaly') {
          // Simulate revenue anomalies
          await Sentry.startSpan(
            {
              name: 'Simulate revenue anomaly',
              op: 'demo.revenue_anomaly',
            },
            async () => {
              // Negative revenue (paying out more than taking in)
              BusinessMetrics.trackMetric(BusinessMetrics.REVENUE_NET, -5000, "currency");
              
              // Unusual deposit/withdrawal ratio
              BusinessMetrics.trackMetric(BusinessMetrics.DEPOSIT_AMOUNT, 1000, "currency");
              BusinessMetrics.trackMetric(BusinessMetrics.WITHDRAWAL_AMOUNT, 6000, "currency");
              
              Sentry.captureMessage(
                "Revenue Alert: Negative daily revenue detected",
                'error'
              );
            }
          );
          
          res.json({ status: "Revenue anomaly triggered", net_revenue: -5000 });
          
        } else {
          // Normal financial metrics
          await Sentry.startSpan(
            {
              name: 'Normal financial metrics',
              op: 'demo.normal',
            },
            async () => {
              BusinessMetrics.trackMetric(BusinessMetrics.PAYMENT_SUCCESS_RATE, 98.5, "percent");
              BusinessMetrics.trackMetric(BusinessMetrics.REVENUE_NET, 2500, "currency");
              BusinessMetrics.trackMetric(BusinessMetrics.DEPOSIT_AMOUNT, 10000, "currency");
              BusinessMetrics.trackMetric(BusinessMetrics.WITHDRAWAL_AMOUNT, 7500, "currency");
            }
          );
          
          res.json({ status: "Normal financial metrics tracked" });
        }
      } catch (error) {
        Sentry.captureException(error);
        res.status(500).json({ error: error.message });
      }
    });
  };
  
  await handler();
});

// Helper function to get daily financial stats
async function getDailyFinancialStats(db) {
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const result = await db.collection('transactions').aggregate([
      {
        $match: {
          timestamp: { $gte: today }
        }
      },
      {
        $group: {
          _id: null,
          totalBets: { $sum: '$bet' },
          totalPayouts: { $sum: '$payout' },
          totalRevenue: { $sum: { $subtract: ['$bet', '$payout'] } },
          transactionCount: { $sum: 1 }
        }
      }
    ]).toArray();
    
    return result[0] || null;
  } catch (error) {
    console.error('Error getting daily stats:', error);
    return null;
  }
}

// IMPORTANT: setupExpressErrorHandler must be AFTER all routes but BEFORE other error handlers
Sentry.setupExpressErrorHandler(app);

// Start server
app.listen(PORT, () => {
  console.log(`Payment Service started on :${PORT}`);
});