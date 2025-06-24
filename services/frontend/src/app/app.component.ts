import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1 style="text-align: center; margin: 40px 0;">🎰 Sentry POC - iGaming Demo</h1>
      <nav style="text-align: center; margin-bottom: 20px;">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" style="margin: 0 10px; color: #4CAF50; text-decoration: none;">Slot Machine</a>
        <a routerLink="/metrics" routerLinkActive="active" style="margin: 0 10px; color: #4CAF50; text-decoration: none;">Business Metrics</a>
      </nav>
      <router-outlet></router-outlet>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'sentry-poc-frontend';
}