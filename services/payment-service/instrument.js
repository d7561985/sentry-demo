const Sentry = require('@sentry/node');
const { nodeProfilingIntegration } = require("@sentry/profiling-node");

// Initialize Sentry BEFORE any other imports
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    nodeProfilingIntegration(),
  ],
  // Tracing
  tracesSampleRate: 1.0, //  Capture 100% of the transactions
  // Set sampling rate for profiling - this is evaluated only once per SDK.init call
  profileSessionSampleRate: 1.0,
  // Trace lifecycle automatically enables profiling during active traces
  profileLifecycle: 'trace',

  // Setting this option to true will send default PII data to Sentry.
  // For example, automatic IP address collection on events
  sendDefaultPii: true,
  profileLifetime: 300,
  environment: 'production',
  debug: true,
});

module.exports = Sentry;