import { provideRouter, RouterModule, Routes } from '@angular/router';
import { importProvidersFrom } from '@angular/core';

// Layouts
import { EmptyLayoutComponent } from '@commons/components/layouts/empty-layout/empty-layout.component';
import { MainLayoutComponent } from '@commons/components/layouts/main-layout/main-layout.component';

// Pages
import { LoginComponent } from '@features/auth/pages/login/login.component';
import { UnauthorizedComponent } from '@features/auth/pages/unauthorized/unauthorized.component';
import { ErrorComponent } from '@commons/components/error/error.component';
import { NotfoundComponent } from '@commons/components/notfound/notfound.component';
import { DashboardComponent } from '@features/fraud/pages/dashboard/dashboard/dashboard.component';
import { HitlComponent } from '@features/fraud/pages/hitl/hitl/hitl.component';
import { TransactionRegisterComponent } from '@features/fraud/pages/transaction/transaction-register/transaction-register.component';
import { HistoryComponent } from '@features/fraud/pages/history/history/history.component';

// Guards
import { rootRedirectGuard } from '@core/guards/rootRedirectGuard';
import { notFoundGuard } from '@core/guards/notfound.guard';
import { authGuard } from '@core/guards/auth.guard';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'home-redirect' },

  {
    path: 'home-redirect',
    canActivate: [rootRedirectGuard],
    component: EmptyLayoutComponent,
  },

  // Rutas públicas
  {
    path: '',
    component: EmptyLayoutComponent,
    children: [
      { path: 'login', component: LoginComponent },
      { path: 'unauthorized', component: UnauthorizedComponent },
      { path: 'error', component: ErrorComponent },
      { path: 'not-found', component: NotfoundComponent },
    ],
  },

  // Rutas privadas
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'hitl', component: HitlComponent },
      { path: 'analyze', component: TransactionRegisterComponent },
      { path: 'history', component: HistoryComponent },
    ],
  },

  { path: '**', canActivate: [notFoundGuard], children: [] },
];

// Export para bootstrap
//export const appRouting = provideRouter(routes);
