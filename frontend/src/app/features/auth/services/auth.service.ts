import { Injectable } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import {
  BehaviorSubject,
  delay,
  firstValueFrom,
  map,
  Observable,
  of,
  tap,
} from 'rxjs';
import { AuthDTO, UserData } from '../interfaces/auth-login-response.interface';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly JWT_KEY = 'app_jwt';
  private readonly USER_KEY = 'app_user';
  private currentUserSubject = new BehaviorSubject<UserData | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.loadUserFromStorage();
  }

  /**
   * Valida token externo y obtiene JWT interno
   */
  login(params: any): Observable<AuthDTO> {
    return this.http
      .post<AuthDTO>(
        `${environment.apiUrl}/api/v1/auth/login`,
        params,
        { observe: 'response' } // importante para obtener status
      )
      .pipe(
        tap((resp: HttpResponse<AuthDTO>) => {
          if (resp.status === 200) {
            this.setSession(resp.body!);
          }
        }),
        map((resp: HttpResponse<AuthDTO>) => resp.body!) // solo emitimos el body
      );
  }

  /**
   * Guarda la sesión (JWT + datos de usuario)
   */
  private setSession(authResponse: AuthDTO): void {
    sessionStorage.setItem(this.JWT_KEY, authResponse.token);
    sessionStorage.setItem(
      this.USER_KEY,
      JSON.stringify(authResponse.userData)
    );
    this.currentUserSubject.next(authResponse.userData);
  }

  /**
   * Carga usuario desde localStorage al iniciar la app
   */
  private loadUserFromStorage(): void {
    const user = sessionStorage.getItem(this.USER_KEY);
    if (user) {
      this.currentUserSubject.next(JSON.parse(user));
    }
  }

  /**
   * Obtiene el JWT actual
   */
  getToken(): string | null {
    try {
      return sessionStorage.getItem(this.JWT_KEY);
    } catch (e) {
      console.log('Exception in getToken', e);
    }
    return null;
  }

  /**
   * Verifica si está autenticado (JWT válido y no expirado)
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    try {
      // Decodificar y verificar expiración
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();
      const isValid = now < exp;

      if (!isValid) {
        this.clearSession();
        return false;
      }

      const minutosRestantes = Math.floor((exp - now) / 60000);
      return true;
    } catch (error) {
      this.clearSession();
      return false;
    }
  }

  /**
   * Cierra sesión
   */
  logout() {
    try {
      // Simulamos la llamada al backend con 1 segundo de demora
      firstValueFrom(of(true).pipe(delay(1000)));
    } catch (error) {
      console.error('Error simulando logout', error);
    } finally {
      // Limpiamos la sesión siempre
      this.clearSession();
    }
  }
  /* async logout(): Promise<void> {
    try {
      // Simulamos la llamada al backend con 1 segundo de demora
      await firstValueFrom(of(true).pipe(delay(1000)));
    } catch (error) {
      console.error('Error simulando logout', error);
    } finally {
      // Limpiamos la sesión siempre
      this.clearSession();
    }
  } */

  /**
   * Limpia la sesión local
   */
  private clearSession(): void {
    sessionStorage.removeItem(this.JWT_KEY);
    sessionStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
  }

  /**
   * Obtiene datos del usuario actual
   */
  getCurrentUser(): UserData | null {
    return this.currentUserSubject.value;
  }

  /**
   * Verifica si el token está próximo a expirar (últimos 5 minutos)
   */
  isTokenExpiringSoon(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000;
      const now = Date.now();
      const minutosRestantes = (exp - now) / 60000;

      return minutosRestantes < 5 && minutosRestantes > 0;
    } catch {
      return false;
    }
  }

  goToUnauthorized() {
    this.router.navigateByUrl('/unauthorized');
  }

  /**
   * Refresca el JWT (opcional, para renovar token antes de que expire)
   */
  async refreshTokens(): Promise<void> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ token: string }>(`/api/auth/refresh`, {})
      );

      sessionStorage.setItem(this.JWT_KEY, response.token);
    } catch (error) {
      this.clearSession();
    }
  }
}
