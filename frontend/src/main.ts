import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { LOCALE_ID, importProvidersFrom } from '@angular/core';
import { registerLocaleData } from '@angular/common';
import localePe from '@angular/common/locales/es-PE';

import { AppComponent } from './app/app.component';
import { AuthInterceptor } from './app/core/interceptor/auth.interceptor';
import { errorInterceptor } from './app/core/interceptor/error.interceptor';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';
import { SHARED_PROVIDERS } from '@commons/utils/shared-modules';
import { NgxSpinnerModule } from 'ngx-spinner';
import { CommonModule } from '@angular/common';
import { provideRouter } from '@angular/router';
import { appRoutes } from './app-routing';

registerLocaleData(localePe, 'es-PE');

bootstrapApplication(AppComponent, {
  providers: [
    provideAnimations(),
    provideRouter(appRoutes),
    provideHttpClient(withInterceptors([AuthInterceptor, errorInterceptor])),
    { provide: LOCALE_ID, useValue: 'es-PE' },
    ...SHARED_PROVIDERS,
    providePrimeNG({
      theme: {
        preset: Aura,
        options: { prefix: 'p', darkModeSelector: false, cssLayer: false },
      },
    }),

    // ✅ Importar módulos que no son standalone con importProvidersFrom
    importProvidersFrom(NgxSpinnerModule.forRoot({ type: 'ball-spin-fade' })),
  ],
}).catch((err) => console.error(err));
