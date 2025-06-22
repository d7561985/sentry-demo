import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import * as Sentry from '@sentry/angular';

import { AppComponent } from './app.component';
import { SlotMachineComponent } from './slot-machine/slot-machine.component';
import { GameService } from './services/game.service';
import { SentryErrorHandler } from './services/sentry-error.handler';

@NgModule({
  declarations: [
    AppComponent,
    SlotMachineComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot([])
  ],
  providers: [
    GameService,
    {
      provide: ErrorHandler,
      useClass: SentryErrorHandler
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }