import { inject } from '@angular/core';
import {
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  CanActivateFn,
} from '@angular/router';

export const notFoundGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  const router = inject(Router);

  const attemptedUrl = state.url;

  sessionStorage.setItem('notFoundUrl', attemptedUrl);
  router.navigate(['/not-found']);

  return false;
};
