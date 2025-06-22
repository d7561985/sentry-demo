import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

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
    // Let Sentry's automatic instrumentation handle the trace headers
    // The BrowserTracing integration will automatically add sentry-trace and baggage headers
    // to requests matching the tracingOrigins pattern
    return this.http.post<SpinResult>(
      `${this.apiUrl}/api/v1/spin`,
      { userId, bet }
    );
  }
}