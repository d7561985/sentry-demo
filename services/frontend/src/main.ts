import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import * as Sentry from '@sentry/angular';
import { BrowserTracing } from '@sentry/tracing';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

// Initialize Sentry
Sentry.init({
  dsn: environment.sentryDsn,
  integrations: [
    new Sentry.BrowserTracing({
      // CRITICAL: This must match your API gateway URL exactly
      // It controls which outgoing requests get trace headers attached
      tracingOrigins: ['localhost', 'http://localhost:8080', /^http:\/\/localhost:8080\/api\//],
      routingInstrumentation: Sentry.routingInstrumentation,
    }),
  ],
  tracesSampleRate: 1.0,
  environment: environment.production ? 'production' : 'development',
  // Debug mode to see trace propagation
  debug: true,
});

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));