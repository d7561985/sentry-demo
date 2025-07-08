import { Component, OnInit, OnDestroy, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { createNewTrace } from '../utils/sentry-traces';
import { BonusRefreshService } from '../services/bonus-refresh.service';

interface BonusProgress {
  has_active_bonus: boolean;
  bonus?: {
    id: string;
    type: string;
    amount: number;
    wagering_required: number;
    wagering_completed: number;
    progress_percentage: number;
    status: string;
    created_at: string;
  };
  balance: {
    real: number;
    bonus: number;
    total: number;
  };
}

@Component({
  selector: 'app-bonus-tracker',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bonus-tracker" *ngIf="bonusData()">
      <h3>Bonus & Balance</h3>
      
      <!-- Balance info always shown -->
      <div class="balance-info">
        <div class="balance-item">
          <span class="label">Real Balance:</span>
          <span class="value">\${{ bonusData()!.balance.real.toFixed(2) }}</span>
        </div>
        <div class="balance-item" *ngIf="bonusData()!.balance.bonus > 0">
          <span class="label">Bonus Balance:</span>
          <span class="value bonus">\${{ bonusData()!.balance.bonus.toFixed(2) }}</span>
        </div>
        <div class="balance-item total">
          <span class="label">Total Balance:</span>
          <span class="value">\${{ bonusData()!.balance.total.toFixed(2) }}</span>
        </div>
      </div>
      
      <!-- Active bonus progress -->
      <div class="bonus-info" *ngIf="bonusData()!.has_active_bonus && bonusData()!.bonus">
        <h4>Active Bonus Progress</h4>
        
        <div class="bonus-details">
          <span class="bonus-type">{{ bonusData()!.bonus!.type | uppercase }} BONUS</span>
          <span class="bonus-amount">\${{ bonusData()!.bonus!.amount }}</span>
        </div>
        
        <div class="progress-bar-container">
          <div class="progress-bar" [style.width.%]="bonusData()!.bonus!.progress_percentage">
            <span class="progress-text">{{ bonusData()!.bonus!.progress_percentage.toFixed(1) }}%</span>
          </div>
        </div>
        
        <div class="wager-info">
          <div class="wager-item">
            <span class="label">Wagered:</span>
            <span class="value">\${{ bonusData()!.bonus!.wagering_completed.toFixed(2) }}</span>
          </div>
          <div class="wager-item">
            <span class="label">Required:</span>
            <span class="value">\${{ bonusData()!.bonus!.wagering_required.toFixed(2) }}</span>
          </div>
          <div class="wager-item">
            <span class="label">Remaining:</span>
            <span class="value">\${{ (bonusData()!.bonus!.wagering_required - bonusData()!.bonus!.wagering_completed).toFixed(2) }}</span>
          </div>
        </div>
        
        <button 
          class="convert-button" 
          *ngIf="bonusData()!.bonus!.status === 'completed'"
          (click)="convertBonus()"
          [disabled]="converting()">
          {{ converting() ? 'Converting...' : 'Convert to Cash' }}
        </button>
        
        <div class="bonus-status" *ngIf="bonusData()!.bonus!.status !== 'completed'">
          <span class="status-label">Status:</span>
          <span class="status-value" [class]="bonusData()!.bonus!.status">{{ bonusData()!.bonus!.status | uppercase }}</span>
        </div>
      </div>
      
      <!-- No bonus - show claim button -->
      <div class="no-bonus" *ngIf="!bonusData()!.has_active_bonus">
        <p>No active bonus. Claim your welcome bonus!</p>
        <button class="claim-button" (click)="claimBonus()" [disabled]="claiming()">
          {{ claiming() ? 'Claiming...' : 'Claim Welcome Bonus ($100)' }}
        </button>
      </div>
      
      <div class="error-message" *ngIf="error()">
        {{ error() }}
      </div>
    </div>
    
    <div class="loading" *ngIf="loading()">
      Loading bonus information...
    </div>
  `,
  styles: [`
    .bonus-tracker {
      background: #1a1a2e;
      border-radius: 8px;
      padding: 20px;
      margin: 20px 0;
      color: #fff;
    }
    
    h3 {
      margin: 0 0 20px 0;
      color: #4fbdba;
    }
    
    h4 {
      margin: 20px 0 15px 0;
      color: #7ec8e3;
      font-size: 1.1em;
    }
    
    .balance-info {
      background: rgba(79, 189, 186, 0.1);
      border-radius: 6px;
      padding: 15px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .balance-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.95em;
    }
    
    .balance-item.total {
      border-top: 1px solid rgba(255, 255, 255, 0.2);
      padding-top: 10px;
      margin-top: 5px;
      font-weight: bold;
    }
    
    .balance-item .value {
      font-weight: 500;
    }
    
    .balance-item .value.bonus {
      color: #ffd700;
    }
    
    .bonus-info {
      background: rgba(126, 200, 227, 0.1);
      border-radius: 6px;
      padding: 15px;
      display: flex;
      flex-direction: column;
      gap: 15px;
    }
    
    .bonus-amount {
      display: flex;
      justify-content: space-between;
      font-size: 1.2em;
    }
    
    .progress-bar-container {
      width: 100%;
      height: 30px;
      background: #0f0f23;
      border-radius: 15px;
      overflow: hidden;
      position: relative;
    }
    
    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #4fbdba 0%, #6fcf97 100%);
      transition: width 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .progress-text {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      font-weight: bold;
      color: #fff;
      text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .wager-info {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
    }
    
    .wager-item {
      display: flex;
      flex-direction: column;
    }
    
    .bonus-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    
    .bonus-type {
      font-size: 0.9em;
      color: #7ec8e3;
      letter-spacing: 1px;
    }
    
    .bonus-amount {
      font-size: 1.5em;
      font-weight: bold;
      color: #ffd700;
    }
    
    .label {
      color: #7c7c8a;
      font-size: 0.9em;
    }
    
    .value {
      color: #fff;
      font-weight: bold;
    }
    
    .expiry-info {
      display: flex;
      justify-content: space-between;
      padding: 10px;
      background: #0f0f23;
      border-radius: 5px;
    }
    
    .convert-button, .claim-button {
      width: 100%;
      padding: 12px;
      background: #4fbdba;
      color: #fff;
      border: none;
      border-radius: 5px;
      font-size: 1.1em;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.3s;
    }
    
    .convert-button:hover, .claim-button:hover {
      background: #3da09d;
    }
    
    .convert-button:disabled, .claim-button:disabled {
      background: #666;
      cursor: not-allowed;
    }
    
    .no-bonus {
      text-align: center;
      padding: 20px;
    }
    
    .no-bonus p {
      margin-bottom: 15px;
      color: #7c7c8a;
    }
    
    .error-message {
      color: #ff6b6b;
      padding: 10px;
      background: rgba(255, 107, 107, 0.1);
      border-radius: 5px;
      margin-top: 10px;
    }
    
    .loading {
      text-align: center;
      padding: 40px;
      color: #7c7c8a;
    }
  `]
})
export class BonusTrackerComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private apiUrl = '/api/v1';
  
  bonusData = signal<BonusProgress | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);
  converting = signal(false);
  claiming = signal(false);
  
  // Computed property for user ID
  private userId = computed(() => {
    // In real app, get from auth service
    return localStorage.getItem('userId') || 'demo-user-1';
  });

  constructor(
    private http: HttpClient,
    private bonusRefreshService: BonusRefreshService
  ) {}

  ngOnInit() {
    // Load initial state
    this.loadBonusProgress();
    
    // Listen for refresh requests instead of using timer
    this.bonusRefreshService.refreshRequested$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        if (!this.converting() && !this.claiming()) {
          this.loadBonusProgress();
        }
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadBonusProgress() {
    createNewTrace(
      'user-action.bonus-tracker.load-progress',
      'http.client',
      async (span) => {
        return new Promise((resolve, reject) => {
          this.http.get<BonusProgress>(`${this.apiUrl}/bonus/progress/${this.userId()}`)
            .subscribe({
              next: (data) => {
                this.bonusData.set(data);
                this.loading.set(false);
                this.error.set(null);
                if (span) {
                  span.setAttribute('bonus.active', data.has_active_bonus);
                  if (data.bonus) {
                    span.setAttribute('bonus.progress', data.bonus.progress_percentage);
                  }
                }
                resolve(data);
              },
              error: (err) => {
                this.error.set('Failed to load bonus information');
                this.loading.set(false);
                reject(err);
              }
            });
        });
      }
    ).catch(err => {
      console.error('Error loading bonus progress:', err);
    });
  }

  claimBonus() {
    this.claiming.set(true);
    this.error.set(null);
    
    createNewTrace(
      'user-action.bonus-tracker.claim-bonus',
      'http.client',
      async (span) => {
        return new Promise((resolve, reject) => {
          const payload = {
            user_id: this.userId(),
            bonus_type: 'WELCOME',
            amount: 100,
            multiplier: 30
          };
          
          this.http.post(`${this.apiUrl}/bonus/claim`, payload)
            .subscribe({
              next: () => {
                this.claiming.set(false);
                // Reload immediately after successful claim
                this.loadBonusProgress();
                resolve(true);
              },
              error: (err) => {
                this.claiming.set(false);
                this.error.set('Failed to claim bonus');
                reject(err);
              }
            });
        });
      }
    ).catch(err => {
      console.error('Error claiming bonus:', err);
    });
  }

  convertBonus() {
    this.converting.set(true);
    this.error.set(null);
    
    createNewTrace(
      'user-action.bonus-tracker.convert-bonus',
      'http.client',
      async (span) => {
        return new Promise((resolve, reject) => {
          this.http.post(`${this.apiUrl}/bonus/convert/${this.userId()}`, {})
            .subscribe({
              next: () => {
                this.converting.set(false);
                // Reload immediately after successful conversion
                this.loadBonusProgress();
                if (span) {
                  span.setAttribute('bonus.converted', true);
                }
                resolve(true);
              },
              error: (err) => {
                this.converting.set(false);
                this.error.set('Failed to convert bonus');
                reject(err);
              }
            });
        });
      }
    ).catch(err => {
      console.error('Error converting bonus:', err);
    });
  }

  formatExpiry(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    
    if (diff <= 0) {
      return 'Expired';
    }
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) {
      return `${days} days, ${hours} hours`;
    }
    return `${hours} hours`;
  }
}