import { Injectable } from '@angular/core';
import { NgxSpinnerService } from 'ngx-spinner';
import { BehaviorSubject, Observable } from 'rxjs';
export interface SpinnerConfig {
  message?: string; // Mensaje personalizado
  fullScreen?: boolean; // Si es pantalla completa o no
  name?: string; // Nombre único del spinner
}

interface SpinnerState {
  name: string;
  message: string;
  fullScreen: boolean;
}
@Injectable({
  providedIn: 'root',
})
export class SpinnerService {
  private defaultSpinner = 'default-spinner';
  private spinnerCounter = 0;
  private readonly DEFAULT_MESSAGE = 'Procesando petición...';

  private activeSpinners = new Map<string, SpinnerState>();
  private defaultMessageSubject = new BehaviorSubject<string>(
    this.DEFAULT_MESSAGE
  );
  public message$ = this.defaultMessageSubject.asObservable();

  constructor(private ngxSpinner: NgxSpinnerService) {}

  /**
   * Mostrar spinner con configuración
   */
  show(config: SpinnerConfig = {}): string {
    // Usar nullish coalescing para evitar undefined
    const message = config.message ?? this.DEFAULT_MESSAGE;
    const fullScreen = config.fullScreen ?? true;
    const name =
      config.name ??
      (fullScreen ? this.defaultSpinner : `spinner-${++this.spinnerCounter}`);

    // Guardar estado del spinner
    this.activeSpinners.set(name, { name, message, fullScreen });

    // Solo actualizar el mensaje observable si es el spinner por defecto (fullscreen)
    if (name === this.defaultSpinner) {
      this.defaultMessageSubject.next(message);
    }

    // Mostrar el spinner
    this.ngxSpinner.show(name, {
      type: 'ball-fussion',
      size: fullScreen ? 'large' : 'medium',
      bdColor: fullScreen ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
      color: '#fff',
      fullScreen: fullScreen,
    });

    return name;
  }

  /**
   * Ocultar spinner específico
   */
  hide(name?: string): void {
    const spinnerName = name ?? this.defaultSpinner;

    this.ngxSpinner.hide(spinnerName);
    this.activeSpinners.delete(spinnerName);

    // Si es el spinner por defecto, resetear mensaje
    if (spinnerName === this.defaultSpinner) {
      this.defaultMessageSubject.next(this.DEFAULT_MESSAGE);
    }
  }

  /**
   * Ocultar todos los spinners
   */
  hideAll(): void {
    this.ngxSpinner.hide();
    this.activeSpinners.clear();
    this.defaultMessageSubject.next(this.DEFAULT_MESSAGE);
  }

  /**
   * Mostrar spinner fullscreen (atajo)
   * Este es el que se usa el 90% del tiempo
   */
  showFullScreen(message: string = this.DEFAULT_MESSAGE): void {
    this.show({
      message,
      fullScreen: true,
      name: this.defaultSpinner,
    });
  }

  /**
   * Ocultar spinner fullscreen (atajo)
   */
  hideFullScreen(): void {
    this.hide(this.defaultSpinner);
  }

  /**
   * Mostrar spinner en un elemento específico
   * IMPORTANTE: Para spinners locales, el mensaje debe ir en el HTML del componente
   */
  showForElement(name: string, message: string = this.DEFAULT_MESSAGE): string {
    return this.show({
      name,
      message,
      fullScreen: false,
    });
  }

  /**
   * Actualizar el mensaje del spinner fullscreen sin ocultarlo
   */
  updateMessage(message: string): void {
    const spinner = this.activeSpinners.get(this.defaultSpinner);
    if (spinner) {
      spinner.message = message;
      this.defaultMessageSubject.next(message);
    }
  }

  /**
   * Obtener el mensaje actual del spinner fullscreen
   */
  getCurrentMessage(): string {
    return this.defaultMessageSubject.value;
  }

  /**
   * Obtener información de un spinner específico
   */
  getSpinnerState(name: string): SpinnerState | undefined {
    return this.activeSpinners.get(name);
  }

  /**
   * Verificar si hay algún spinner activo
   */
  hasActiveSpinners(): boolean {
    return this.activeSpinners.size > 0;
  }

  /**
   * Verificar si un spinner específico está activo
   */
  isActive(name: string = this.defaultSpinner): boolean {
    return this.activeSpinners.has(name);
  }

  /**
   * Obtener todos los spinners activos
   */
  getActiveSpinners(): SpinnerState[] {
    return Array.from(this.activeSpinners.values());
  }
}
