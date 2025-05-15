import {bootstrapApplication, provideClientHydration, withEventReplay} from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import {provideHttpClient, withFetch} from '@angular/common/http';
import {provideZoneChangeDetection} from '@angular/core';
import {provideRouter} from '@angular/router';
import {routes} from './app/app.routes';
import {PanelProductosComponent} from './app/components/panel-productos/panel-productos.component';

bootstrapApplication(AppComponent,  {
  providers: [
      provideHttpClient(withFetch()),
    provideZoneChangeDetection({ eventCoalescing: true }), provideRouter(routes), provideClientHydration(withEventReplay())],
})
  .catch((err) => console.error(err));
