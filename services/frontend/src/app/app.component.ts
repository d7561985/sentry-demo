import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1 style="text-align: center; margin: 40px 0;">🎰 Sentry POC - iGaming Demo</h1>
      <app-slot-machine></app-slot-machine>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'sentry-poc-frontend';
}