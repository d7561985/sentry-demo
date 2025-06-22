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
      
      <button 
        class="spin-button" 
        (click)="spin()"
        [disabled]="isSpinning || balance < 10">
        {{ isSpinning ? 'Spinning...' : 'SPIN ($10)' }}
      </button>
      
      <div class="result" *ngIf="lastResult">
        <div *ngIf="lastResult.win">
          🎉 You won $<span>{{lastResult.payout}}</span>!
        </div>
        <div *ngIf="!lastResult.win">
          Better luck next time!
        </div>
      </div>
      
      <div class="error" *ngIf="error">
        ❌ Error: {{ error }}
      </div>
      
      <div style="margin-top: 40px; opacity: 0.7;">
        <small>User ID: {{ userId }}</small>
      </div>
    </div>
  `,
  styles: []
})
export class SlotMachineComponent implements OnInit {
  balance = 1000;
  isSpinning = false;
  lastResult: any = null;
  error: string | null = null;
  userId = 'demo-user-' + Math.floor(Math.random() * 1000);

  constructor(private gameService: GameService) {}

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
        this.lastResult = result;
        this.balance = result.newBalance;
        
        // Add custom context
        transaction.setTag('win', result.win);
        transaction.setTag('payout', result.payout);
      }
    } catch (error: any) {
      this.error = error.message || 'Something went wrong!';
      transaction.setStatus('internal_error');
      Sentry.captureException(error);
    } finally {
      this.isSpinning = false;
      transaction.finish();
    }
  }
}