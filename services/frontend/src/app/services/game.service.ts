import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import * as Sentry from '@sentry/angular';

export interface SpinResult {
  win: boolean;
  payout: number;
  newBalance: number;
  symbols: string[];
}

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  spin(userId: string, bet: number): Observable<SpinResult> {
    const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();
    const span = transaction?.startChild({
      op: 'http.client',
      description: 'POST /api/v1/spin'
    });

    // Get trace headers for distributed tracing
    const traceHeader = span ? span.toTraceparent() : '';
    
    // For Sentry v7, we need to construct baggage manually
    let baggageHeader = '';
    if (transaction) {
      const traceId = transaction.traceId;
      const client = Sentry.getCurrentHub().getClient();
      const dsn = client?.getDsn();
      const publicKey = dsn?.publicKey || '';
      baggageHeader = `sentry-trace_id=${traceId},sentry-public_key=${publicKey},sentry-sample_rate=1`;
    }

    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'sentry-trace': traceHeader,
      'baggage': baggageHeader
    });

    return this.http.post<SpinResult>(
      `${this.apiUrl}/api/v1/spin`,
      { userId, bet },
      { headers }
    ).pipe(
      finalize(() => span?.finish())
    );
  }
}