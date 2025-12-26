import { inject } from '@angular/core';
import { Router, ActivatedRouteSnapshot, CanActivateFn } from '@angular/router';
import { AuthService } from '@features/auth/services/auth.service';

export const authGuard: CanActivateFn = async (
  route: ActivatedRouteSnapshot
) => {
  const router = inject(Router);
  const authService = inject(AuthService);

  if (authService.isAuthenticated()) {
    return true;
  }

  router.navigate(['/unauthorized']);
  return false;
};
