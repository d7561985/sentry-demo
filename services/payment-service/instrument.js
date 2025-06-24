const Sentry = require('@sentry/node');

// Initialize Sentry BEFORE any other imports
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: 'development',
  debug: true,
});

module.exports = Sentry;