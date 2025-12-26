import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { MessageService } from 'primeng/api';
import { HelperService } from '@commons/services/helper.service';
import { AuthService } from '@features/auth/services/auth.service';
import { MessageType } from '@commons/constants/MessageType';

export const errorInterceptor: HttpInterceptorFn = (request, next) => {
  const helper = inject(HelperService);
  const auth = inject(AuthService);
  const messageService = inject(MessageService);

  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      //loading.stop();
      const baseUrl = new URL(request.url).origin;
      // Errores normales
      return handleHttpError(error, helper, auth);
    })
  );
};

/* -------------------------------------------------------
   Manejo estandarizado de errores backend
-------------------------------------------------------- */
function handleHttpError(error: HttpErrorResponse, helper: any, auth: any) {
  const body = normalizeBackendError(error.error);

  switch (error.status) {
    case 0:
      helper.getErrorAlert(
        `No se pudo conectar con el servidor.<p class="mt-2">Verifica tu conexión e inténtalo nuevamente.</p>`
      );
      break;

    case 400:
      helper.getErrorAlert(body.mensaje);
      break;

    case 401:
    case 403:
      helper.showMessage(
        MessageType.ERROR,
        'Por favor, verifique sus credenciales.',
        'Error al iniciar sesión'
      );
      auth.logout();
      break;

    case 404:
      helper.getErrorAlert(body.mensaje || 'Recurso no encontrado.');
      break;

    case 422:
    case 409:
      helper.showMessage(MessageType.ERROR, body.mensaje);
      break;

    case 500:
      helper.getErrorAlert(undefined, body.source);
      break;

    default:
      helper.getErrorAlert(body.mensaje || 'Ocurrió un error inesperado.');
      break;
  }

  return throwError(() => error);
}

/* -------------------------------------------------------
   Normaliza la estructura del error del backend
-------------------------------------------------------- */
function normalizeBackendError(error: any): {
  mensaje: string;
  source?: string;
} {
  let mensaje = 'Ocurrió un error';
  let source = '';

  if (!error) return { mensaje, source };

  if (error.detail) {
    if (typeof error.detail === 'string') {
      mensaje = error.detail;
    } else if (typeof error.detail === 'object' && error.detail.message) {
      mensaje = error.detail.message;
    }
  } else if (error.message) {
    mensaje = error.message;
  }

  if (error.source) source = error.source;

  return { mensaje, source };
}

/* -------------------------------------------------------
   Función helper para convertir Blob JSON a objeto
-------------------------------------------------------- */
function blobToJson(blob: Blob): Promise<any> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        resolve(JSON.parse(reader.result as string));
      } catch (e) {
        reject(e);
      }
    };
    reader.onerror = (e) => reject(e);
    reader.readAsText(blob);
  });
}
