import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import * as Sentry from '@sentry/angular';

import { AppComponent } from './app.component';
import { SlotMachineComponent } from './slot-machine/slot-machine.component';
import { BusinessMetricsComponent } from './business-metrics/business-metrics.component';
import { GameService } from './services/game.service';
import { SentryErrorHandler } from './services/sentry-error.handler';

@NgModule({
    imports: [
        BrowserModule,
        AppComponent,
        SlotMachineComponent,
        BusinessMetricsComponent,
        RouterModule.forRoot([
            { path: '', component: SlotMachineComponent },
            { path: 'metrics', component: BusinessMetricsComponent }
        ])
    ],
    providers: [
        GameService,
        {
            provide: ErrorHandler,
            useClass: SentryErrorHandler
        },
        provideHttpClient(withInterceptorsFromDi()),
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }