import { Component, OnInit } from '@angular/core';
import * as Sentry from '@sentry/angular';
import { GameService } from '../services/game.service';

@Component({
  selector: 'app-slot-machine',
  template: `
    <div class="slot-machine">
      <h2>🎰 Simple Slot Machine</h2>
      
      <div class="balance">
        Balance: $<span>{{balance}}</span>
      </div>

      <!-- 3 Reels in a Row -->
      <div class="slots-container">
        <div class="slot-window" *ngFor="let reel of reels; let i = index">
          <div class="reel" [class.spinning]="isSpinning">
            <div class="symbol-strip" *ngIf="isSpinning">
              <div class="symbol" *ngFor="let symbol of spinningSymbols">{{ symbol }}</div>
              <!-- Duplicate symbols for seamless loop -->
              <div class="symbol" *ngFor="let symbol of spinningSymbols">{{ symbol }}</div>
            </div>
            <div class="symbol static" *ngIf="!isSpinning">{{ reel }}</div>
          </div>
        </div>
      </div>
      
      <button 
        class="spin-button" 
        (click)="spin()"
        [disabled]="isSpinning || balance < 10">
        {{ isSpinning ? 'Spinning...' : 'SPIN ($10)' }}
      </button>
      
      <div class="result" *ngIf="lastResult && !isSpinning">
        <div *ngIf="lastResult.win" class="win">
          🎉 You won $<span>{{lastResult.payout}}</span>!
        </div>
        <div *ngIf="!lastResult.win" class="lose">
          Better luck next time!
        </div>
      </div>
      
      <div class="error" *ngIf="error">
        ❌ Error: {{ error }}
      </div>
      
      <div style="margin-top: 40px; opacity: 0.7;">
        <small>User ID: {{ userId }}</small>
      </div>
      
      <!-- Debug Panel for Error Scenarios -->
      <div class="debug-panel">
        <button class="debug-toggle" (click)="debugPanelOpen = !debugPanelOpen">
          🐛 {{ debugPanelOpen ? 'Hide' : 'Show' }} Debug Panel
        </button>
        
        <div class="debug-content" *ngIf="debugPanelOpen">
          <h3>Error Scenario Triggers</h3>
          
          <div class="debug-section">
            <h4>Frontend Errors</h4>
            <button class="debug-button" (click)="triggerPromiseRejection()">
              💥 Trigger Promise Rejection
            </button>
            <button class="debug-button" (click)="triggerComponentError()">
              🔥 Trigger Component Error
            </button>
          </div>
          
          <div class="debug-section">
            <h4>Backend Errors</h4>
            <button class="debug-button" (click)="triggerGatewayPanic()">
              ⚠️ Trigger Gateway Panic
            </button>
            <button class="debug-button" (click)="triggerAuthError()">
              🔒 Trigger 401 Auth Error
            </button>
          </div>
          
          <div class="debug-section">
            <h4>Performance Issues</h4>
            <button class="debug-button" (click)="triggerN1Query()">
              🐌 Trigger N+1 Query
            </button>
            <button class="debug-button" (click)="triggerCPUSpike()">
              🔥 Trigger CPU Spike
            </button>
            <button class="debug-button" (click)="triggerSlowAggregation()">
              📊 Trigger Slow Analytics
            </button>
          </div>
          
          <div class="debug-status" *ngIf="debugStatus">
            Status: {{ debugStatus }}
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .slot-machine {
      text-align: center;
      padding: 20px;
      max-width: 600px;
      margin: 0 auto;
    }

    .balance {
      font-size: 24px;
      margin-bottom: 30px;
      color: #4CAF50;
    }

    .slots-container {
      display: flex;
      justify-content: center;
      gap: 10px;
      margin: 0 auto 30px;
    }

    .slot-window {
      width: 120px;
      height: 120px;
      background: #2a2a2a;
      border: 5px solid #444;
      border-radius: 15px;
      overflow: hidden;
      position: relative;
      box-shadow: 
        inset 0 0 20px rgba(0,0,0,0.5),
        0 0 20px rgba(255,255,255,0.1);
    }

    .reel {
      height: 100%;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .symbol-strip {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
    }

    .reel.spinning .symbol-strip {
      animation: scroll 0.8s linear infinite;
    }

    @keyframes scroll {
      0% {
        transform: translateY(-720px); /* Start above viewport */
      }
      100% {
        transform: translateY(0); /* Move down to original position */
      }
    }

    .symbol {
      font-size: 80px;
      height: 120px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
    }

    .symbol.static {
      position: absolute;
      top: 0;
      left: 0;
    }

    .spin-button {
      background: #FF6B6B;
      color: white;
      border: none;
      padding: 15px 40px;
      font-size: 20px;
      font-weight: bold;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }

    .spin-button:hover:not(:disabled) {
      background: #FF5252;
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
    }

    .spin-button:disabled {
      background: #666;
      cursor: not-allowed;
      box-shadow: none;
    }

    .result {
      margin-top: 20px;
      font-size: 18px;
      font-weight: bold;
      min-height: 30px;
    }

    .result .win {
      color: #4CAF50;
      animation: pulse 0.5s ease-in-out 2;
    }

    .result .lose {
      color: #999;
    }

    @keyframes pulse {
      0%, 100% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.1);
      }
    }

    .error {
      color: #F44336;
      margin-top: 10px;
    }

    /* Debug Panel Styles */
    .debug-panel {
      margin-top: 40px;
      padding: 20px;
      background: #1a1a1a;
      border-radius: 10px;
      border: 2px solid #333;
    }

    .debug-toggle {
      background: #666;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s;
    }

    .debug-toggle:hover {
      background: #777;
    }

    .debug-content {
      margin-top: 20px;
      text-align: left;
    }

    .debug-content h3 {
      color: #ff9800;
      margin-bottom: 15px;
      text-align: center;
    }

    .debug-section {
      margin-bottom: 20px;
      padding: 15px;
      background: #252525;
      border-radius: 8px;
    }

    .debug-section h4 {
      color: #4CAF50;
      margin-bottom: 10px;
    }

    .debug-button {
      display: block;
      width: 100%;
      margin: 8px 0;
      padding: 10px;
      background: #3f51b5;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.3s;
    }

    .debug-button:hover {
      background: #303f9f;
      transform: translateY(-1px);
    }

    .debug-status {
      margin-top: 15px;
      padding: 10px;
      background: #2196F3;
      color: white;
      border-radius: 5px;
      text-align: center;
    }
  `]
})
export class SlotMachineComponent implements OnInit {
  balance = 1000;
  isSpinning = false;
  lastResult: any = null;
  error: string | null = null;
  userId = 'demo-user-' + Math.floor(Math.random() * 1000);
  reels: string[] = ['🍒', '🍋', '🍊'];
  spinningSymbols: string[] = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎'];
  
  // Debug panel properties
  debugPanelOpen = false;
  debugStatus: string | null = null;

  constructor(private gameService: GameService) {}
  
  get apiUrl(): string {
    return (this.gameService as any).apiUrl;
  }

  ngOnInit(): void {
    // Set user context for Sentry
    Sentry.setUser({
      id: this.userId,
      username: 'demo_player'
    });
  }

  async spin(): Promise<void> {
    this.isSpinning = true;
    this.error = null;
    
    // Start a transaction for the spin action
    const transaction = Sentry.startTransaction({
      name: 'slot-machine-spin',
      op: 'user-action'
    });
    
    Sentry.getCurrentHub().configureScope(scope => scope.setSpan(transaction));
    
    try {
      const result = await this.gameService.spin(this.userId, 10).toPromise();
      if (result) {
        // Simulate spinning animation duration
        setTimeout(() => {
          this.lastResult = result;
          this.balance = result.newBalance;
          // Show the result symbols (use first 3 or repeat if less)
          if (result.symbols && result.symbols.length > 0) {
            this.reels = [
              result.symbols[0] || '🍒',
              result.symbols[1] || result.symbols[0] || '🍒',
              result.symbols[2] || result.symbols[0] || '🍒'
            ];
          }
          this.isSpinning = false;
        }, 2000);
        
        // Add custom context
        transaction.setTag('win', result.win);
        transaction.setTag('payout', result.payout);
      }
    } catch (error: any) {
      this.error = error.message || 'Something went wrong!';
      this.isSpinning = false;
      transaction.setStatus('internal_error');
      Sentry.captureException(error);
    } finally {
      transaction.finish();
    }
  }
  
  // Debug Panel Methods for Error Scenarios
  
  async triggerPromiseRejection(): Promise<void> {
    this.debugStatus = 'Triggering unhandled promise rejection...';
    
    // Create a promise that will reject after 1 second
    // NOT catching this error intentionally to demonstrate unhandled rejection
    setTimeout(() => {
      // This promise rejection will be unhandled
      Promise.reject(new Error('Unhandled promise rejection from debug panel'));
      this.debugStatus = 'Promise rejection triggered! Check Sentry dashboard.';
    }, 1000);
  }
  
  triggerComponentError(): void {
    this.debugStatus = 'Triggering component error...';
    
    // Intentionally throw an error to be caught by Angular ErrorHandler
    setTimeout(() => {
      throw new Error('Component error triggered from debug panel');
    }, 100);
  }
  
  async triggerGatewayPanic(): Promise<void> {
    this.debugStatus = 'Triggering gateway panic...';
    
    try {
      // Use special userId that triggers panic in gateway
      const response = await fetch(`${this.apiUrl}/api/v1/debug/panic/panic-test`, {
        method: 'GET'
        // Sentry will automatically add trace headers via BrowserTracing
      });
      
      if (!response.ok) {
        this.debugStatus = 'Gateway panic triggered! Check Sentry for Go panic.';
      }
    } catch (error) {
      this.debugStatus = 'Gateway panic triggered (connection lost)';
    }
  }
  
  async triggerAuthError(): Promise<void> {
    this.debugStatus = 'Triggering 401 auth error...';
    
    try {
      // Call user service with invalid token
      const response = await fetch(`${this.apiUrl}/api/v1/user/${this.userId}`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer invalid-token'
          // Sentry will automatically add trace headers via BrowserTracing
        }
      });
      
      if (response.status === 401) {
        this.debugStatus = '401 Auth error triggered! Check Sentry dashboard.';
      } else {
        this.debugStatus = `Unexpected response: ${response.status}`;
      }
    } catch (error) {
      this.debugStatus = 'Error calling user service';
    }
  }
  
  // Performance Issue Triggers
  
  async triggerN1Query(): Promise<void> {
    this.debugStatus = 'Triggering N+1 query problem...';
    
    const transaction = Sentry.startTransaction({
      name: 'debug-n1-query',
      op: 'http'
    });
    
    try {
      const response = await fetch(`${this.apiUrl}/api/v1/user/${this.userId}/history`, {
        method: 'GET'
      });
      
      if (response.ok) {
        const data = await response.json();
        this.debugStatus = `N+1 query executed! Found ${data.totalGames} games. Check Performance in Sentry.`;
      } else {
        this.debugStatus = `Failed to trigger N+1: ${response.status}`;
      }
    } catch (error) {
      this.debugStatus = 'Error triggering N+1 query';
      Sentry.captureException(error);
    } finally {
      transaction.finish();
    }
  }
  
  async triggerCPUSpike(): Promise<void> {
    this.debugStatus = 'Triggering CPU spike in game engine...';
    
    const transaction = Sentry.startTransaction({
      name: 'debug-cpu-spike',
      op: 'http'
    });
    
    try {
      // Make a spin request with cpu_intensive flag
      const response = await fetch(`${this.apiUrl}/api/v1/spin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userId: this.userId,
          bet: 10,
          cpu_intensive: true  // This triggers the CPU spike
        })
      });
      
      if (response.ok) {
        this.debugStatus = 'CPU spike completed! Check Performance → Game Engine in Sentry.';
      } else {
        this.debugStatus = `Failed to trigger CPU spike: ${response.status}`;
      }
    } catch (error) {
      this.debugStatus = 'Error triggering CPU spike';
      Sentry.captureException(error);
    } finally {
      transaction.finish();
    }
  }
  
  async triggerSlowAggregation(): Promise<void> {
    this.debugStatus = 'Triggering slow MongoDB aggregation...';
    
    const transaction = Sentry.startTransaction({
      name: 'debug-slow-aggregation',
      op: 'http'
    });
    
    try {
      // Call analytics service for daily stats
      const response = await fetch(`http://localhost:8084/api/v1/analytics/daily-stats?days=30`, {
        method: 'GET'
      });
      
      if (response.ok) {
        const data = await response.json();
        this.debugStatus = `Slow aggregation completed! Processed ${data.days_returned} days. Check Performance → Analytics in Sentry.`;
      } else {
        this.debugStatus = `Failed to trigger aggregation: ${response.status}`;
      }
    } catch (error) {
      this.debugStatus = 'Error triggering slow aggregation - is analytics service running?';
      Sentry.captureException(error);
    } finally {
      transaction.finish();
    }
  }
}