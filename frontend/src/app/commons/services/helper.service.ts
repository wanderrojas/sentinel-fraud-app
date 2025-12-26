import { inject, Injectable } from '@angular/core';
//import * as CryptoJS from 'crypto-js';
import Swal from 'sweetalert2';
import { FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageType } from '../constants/MessageType';
import { MessageService } from 'primeng/api';
import { Toast } from 'primeng/toast';

@Injectable({
  providedIn: 'root',
})
export class HelperService {
  messageService = inject(MessageService);

  router = inject(Router);

  validateForm(
    form: FormGroup,
    message = 'Llene los campos obligatorios (*) para continuar'
  ) {
    if (!form.valid) {
      this.messageService.add({
        severity: 'error',
        summary: 'Validación',
        detail: message,
      });
      for (const control of Object.keys(form.controls)) {
        form.controls[control].markAsTouched();
      }
      return false;
    } else {
      return true;
    }
  }

  isInvalid(controlName: string, form: FormGroup): boolean {
    const control = form.get(controlName);
    return control ? control.invalid && control.touched : false;
  }

  getAlertMessage(
    message: string = `¡Ups! algo sucedió. <br>Por favor intenta nuevamente.`,
    title = ''
  ) {
    return Swal.fire({
      title: title,
      icon: 'warning',
      allowOutsideClick: false,
      html: message,
      confirmButtonText: `<i class="fa-solid fa-rotate-right"></i> Vuelve a intentar nuevamente`,
      confirmButtonColor: '#6365f1',
    });
  }

  getPrimeNgMessage(
    severity: MessageType,
    htmlContent: string,
    options?: { showIcon?: boolean }
  ): string {
    const showIcon = options?.showIcon ?? true;

    const iconMap: Record<MessageType, string> = {
      [MessageType.INFO]: 'info-circle',
      [MessageType.WARN]: 'exclamation-triangle',
      [MessageType.ERROR]: 'times-circle',
      [MessageType.SUCCESS]: 'check',
    };

    const iconHtml = showIcon
      ? `<span class="p-message-icon pi pi-${iconMap[severity]}"></span>`
      : '';

    return `
    <div class="p-message p-component p-message-${severity}">
      <div class="p-message-wrapper flex align-items-center ">
        ${iconHtml}
        <span class="p-message-text">${htmlContent}</span>
      </div>
    </div>
  `;
  }

  /**
   * Devuelve un objeto compatible con messageService.add de PrimeNG.
   * @param severity Tipo de mensaje ('info', 'warn', 'error', 'success')
   * @param summary Título del mensaje
   * @param detail Texto del mensaje
   */
  buildMessagePrime(severity: MessageType, detail: string, summary?: string) {
    // Si no se pasa summary, usamos el tipo de severidad como título
    const defaultSummaryMap: Record<MessageType, string> = {
      [MessageType.INFO]: 'Info',
      [MessageType.WARN]: 'Advertencia',
      [MessageType.ERROR]: 'Error',
      [MessageType.SUCCESS]: 'Éxito',
    };

    return {
      severity: severity.toLowerCase(), // PrimeNG espera 'info', 'warn', 'error', 'success'
      summary: summary ?? defaultSummaryMap[severity],
      detail,
    };
  }

  /**
   * Muestra un mensaje en pantalla usando messageService.add de PrimeNG.
   * @param severity Tipo de mensaje ('info', 'warn', 'error', 'success')
   * @param detail Texto del mensaje
   * @param summary Título opcional del mensaje
   */
  showMessage(severity: MessageType, detail: string, summary?: string) {
    const defaultSummaryMap: Record<MessageType, string> = {
      [MessageType.INFO]: 'Info',
      [MessageType.WARN]: 'Advertencia',
      [MessageType.ERROR]: 'Error',
      [MessageType.SUCCESS]: 'Éxito',
    };

    this.messageService.add({
      severity: severity.toLowerCase(),
      summary: summary ?? defaultSummaryMap[severity],
      detail,
      life: 3000, // duración en ms, opcional
    });
  }

  getAlertMessage409(
    message: string = `¡Ups! algo sucedió. <br>Por favor intenta nuevamente.`,
    title = ''
  ) {
    return Swal.fire({
      title: title,
      icon: 'warning',
      allowOutsideClick: false,
      html: message,
      confirmButtonText: `<i class="fa-solid fa-rotate-right"></i> Vuelve a intentar nuevamente`,
      confirmButtonColor: '#6365f1',
      customClass: {
        popup: 'swal-wide-409',
      },
    });
  }

  objectToFormData(obj: any, formData: FormData) {
    for (let key in obj) {
      formData.append(key, obj[key]);
    }
  }
  getErrorAlert(
    message: string = `Inténtalo de nuevo, si el error persiste, prueba recargando la página.`,
    title = '¡Ups! algo sucedió.'
  ) {
    return Swal.fire({
      title: title,
      icon: 'error',
      allowOutsideClick: false,
      html: message,
      confirmButtonText: `<i class="fa-solid fa-rotate-right"></i> Vuelve a intentar nuevamente`,
      confirmButtonColor: '#6365f1',
    });
  }

  getSuccessAlert(
    title: string,
    message: string,
    confirmButtonText: string = ''
  ) {
    return Swal.fire({
      allowOutsideClick: false,
      title: title,
      icon: 'success',
      html: message,
      confirmButtonColor: '#6365f1',
      confirmButtonText: confirmButtonText,
    });
  }

  /**
   * Convierte un objeto en un query string para URLs.
   * @returns string tipo "key=value&key2=value2"
   */
  toQueryParams(obj: Record<string, any>): string {
    return Object.keys(obj)
      .map(
        (k) => `${encodeURIComponent(k)}=${encodeURIComponent(obj[k] ?? '')}`
      )
      .join('&');
  }

  /**
   * Convierte un objeto JSON en una cadena de parámetros de URL.
   * Ejemplo: { a: 1, b: "x" } -> "a=1&b=x"
   */
  objToQueryString(obj: Record<string, any>): string {
    if (!obj || typeof obj !== 'object') return '';

    const params = new URLSearchParams();

    Object.entries(obj).forEach(([key, value]) => {
      if (value === undefined || value === null) {
        params.append(key, '');
      } else if (Array.isArray(value)) {
        value.forEach((v) => params.append(key, String(v)));
      } else if (typeof value === 'object') {
        Object.entries(value).forEach(([subKey, subVal]) => {
          params.append(`${key}[${subKey}]`, String(subVal ?? ''));
        });
      } else {
        params.append(key, String(value));
      }
    });

    return params.toString();
  }
}
