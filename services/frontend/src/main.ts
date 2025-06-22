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
      tracingOrigins: ['localhost', environment.apiUrl, /^\//],
      routingInstrumentation: Sentry.routingInstrumentation,
    }),
  ],
  tracesSampleRate: 1.0,
  environment: environment.production ? 'production' : 'development',
});

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch(err => console.error(err));