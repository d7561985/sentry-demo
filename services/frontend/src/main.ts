import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import * as Sentry from '@sentry/angular';
import { BrowserTracing } from '@sentry/tracing';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

// Initialize Sentry with Session Replay
Sentry.init({
  dsn: environment.sentryDsn,
  release: (environment as any).version || '1.0.0',
  integrations: [
    new Sentry.BrowserTracing({
      // CRITICAL: This must match your API gateway URL exactly
      // It controls which outgoing requests get trace headers attached
      tracingOrigins: ['localhost', 'http://localhost:8080', /^http:\/\/localhost:8080\/api\//],
      routingInstrumentation: Sentry.routingInstrumentation,
    }),
    new Sentry.Replay({
      // Mask all text content for privacy (default)
      maskAllText: false, // For demo, show text
      // Block all media elements
      blockAllMedia: false,
      // Network details
      networkDetailAllowUrls: ['http://localhost:8080'],
      // Privacy settings for demo
      maskAllInputs: false, // Show input values in demo
      // Maximum replay duration (5 minutes)
      maxReplayDuration: 300000,
    }),
  ],
  tracesSampleRate: 1.0,
  // Session Replay sample rates
  replaysSessionSampleRate: 1.0, // 100% for demo
  replaysOnErrorSampleRate: 1.0, // 100% for errors
  environment: environment.production ? 'production' : 'development',
  // Debug mode to see trace propagation (disable in production)
  debug: !environment.production,
});

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));