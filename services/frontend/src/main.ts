import { bootstrapApplication } from '@angular/platform-browser';
import { enableProdMode } from '@angular/core';
import * as Sentry from '@sentry/angular';

import { AppComponent } from './app/app.component';
import { appConfig } from './app.config';
import { environment } from './environments/environment';

// Initialize Sentry SDK v9 with Session Replay
Sentry.init({
  dsn: environment.sentryDsn,
  release: environment.version || '1.0.0',
  // Setting this option to true will send default PII data to Sentry.
  // For example, automatic IP address collection on events
  sendDefaultPii: true,
  integrations: [
    // BrowserTracing integration for Angular
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration({
      // Mask all text content for privacy (default)
      maskAllText: false, // For demo, show text
      // Block all media elements
      blockAllMedia: false,
      // Network details
      networkDetailAllowUrls: ['http://localhost:8080'],
      // Privacy settings for demo
      maskAllInputs: false, // Show input values in demo
    }),
  ],
  // Trace propagation configuration is now at the root level
  tracePropagationTargets: ['localhost', 'http://localhost:8080', /^http:\/\/localhost:8080\/api\//],
  tracesSampleRate: 1.0,
  // Session Replay sample rates are now at root level
  replaysSessionSampleRate: 1.0, // 100% for demo
  replaysOnErrorSampleRate: 1.0, // 100% for errors
  environment: environment.production ? 'production' : 'development',
  // Debug mode to see trace propagation (disable in production)
  debug: !environment.production,
});

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err));