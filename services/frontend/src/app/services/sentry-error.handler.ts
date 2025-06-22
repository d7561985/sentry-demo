import { ErrorHandler, Injectable } from '@angular/core';
import * as Sentry from '@sentry/angular';

@Injectable()
export class SentryErrorHandler implements ErrorHandler {
  handleError(error: Error): void {
    // Log to console for debugging
    console.error('Angular ErrorHandler caught:', error);
    
    // Add custom context for Angular errors
    Sentry.withScope(scope => {
      scope.setTag('error_type', 'angular_error_handler');
      scope.setLevel('error');
      scope.setContext('angular_error', {
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });
      
      // Capture the exception with Sentry
      Sentry.captureException(error);
    });
    
    // You can add custom error handling logic here
    // For example, show a user-friendly error message
  }
}