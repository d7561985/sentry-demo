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
}