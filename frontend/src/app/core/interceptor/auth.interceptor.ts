import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { environment } from '@envs/environment';
import { AuthService } from '@features/auth/services/auth.service';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Excluir endpoints públicos
  const publicEndpoints = ['/api/auth/login'];
  const isPublicEndpoint = publicEndpoints.some((url) => req.url.includes(url));

  const headers: Record<string, string> = {
    'X-API-Key': environment.apiKey,
  };

  if (!isPublicEndpoint) {
    const token = authService.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  req = req.clone({ setHeaders: headers });

  return next(req);
};
