import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '@envs/environment';
import { AuthService } from '@features/auth/services/auth.service';
import { Observable } from 'rxjs';
import { CaseHitl } from '../interfaces/case-hitl.interface';
import {
  DecisionResponse,
  Statistics,
  HITLCase,
  TransactionAnalysisRequest,
} from '../interfaces/fraud.models';
import { ReviewResponse } from '../interfaces/review-responseinterface';
import { TransactionDetail } from '../interfaces/transaction-detail.interface';
import { TransactionStreamEvent } from '../pages/transaction/transaction-register/transaction-register.component';

@Injectable({
  providedIn: 'root',
})
export class FraudService {
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl; //+ '/api/v1';

  analyzeTransaction(
    request: any // TransactionAnalysisRequest
  ): Observable<DecisionResponse> {
    return this.http.post<DecisionResponse>(
      `${this.apiUrl}/transactions/analyze`,
      request
    );
  }

  // ============================================
  // HISTORY
  // ============================================

  getTransactionHistory(params: any) {
    let url = `${this.apiUrl}/api/v1/history/transactions?${params}`;
    return this.http.get<any>(url);
  }

  /**
   * Obtiene los detalles completos de una transacción, incluidos los logs de análisis.
   * @param transaction_id ID de la transacción a consultar
   * @returns Información completa de la transacción
   */
  getTransactionDetail(transaction_id: string) {
    let url = `${this.apiUrl}/api/v1/history/transactions/${transaction_id}`;
    return this.http.get<TransactionDetail>(url);
  }

  getStatistics(): Observable<Statistics> {
    return this.http.get<Statistics>(
      `${this.apiUrl}/api/v1/history/statistics`
    );
  }

  // ============================================
  // HITL (Human-in-the-Loop)
  // ============================================

  getPendingCases(): Observable<HITLCase[]> {
    return this.http.get<HITLCase[]>(`${this.apiUrl}/api/v1/hitl/pending`);
  }

  getAllCases(status?: string): Observable<CaseHitl[]> {
    let url = `${this.apiUrl}/api/v1/hitl/cases`;
    if (status) {
      url += `?status=${status}`;
    }
    return this.http.get<CaseHitl[]>(url);
  }

  getCase(caseId: string): Observable<HITLCase> {
    return this.http.get<HITLCase>(
      `${this.apiUrl}/api/v1/hitl/cases/${caseId}`
    );
  }

  reviewCase(params: any, caseId: string): Observable<any> {
    return this.http.post<ReviewResponse>(
      `${this.apiUrl}/api/v1/hitl/cases/${caseId}/review`,
      params
    );
  }

  getHITLStatistics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/v1/hitl/statistics`);
  }

  /** Streaming de análisis de transacción */
  analyzeWithStreaming(
    request: TransactionAnalysisRequest
  ): Observable<TransactionStreamEvent> {
    return new Observable((subscriber) => {
      const url = `${environment.apiUrl}/api/v1/transactions/analyze-stream`;
      const headers = this.buildHeaders();

      fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(request),
      })
        .then((response) => {
          if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          const readStream = () => {
            reader
              ?.read()
              .then(({ done, value }) => {
                if (done) {
                  subscriber.complete();
                  return;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                lines.forEach((line) => {
                  if (!line.startsWith('data: ')) return;
                  const data = line.substring(6).trim();
                  if (!data) return;

                  try {
                    const event = JSON.parse(data);
                    subscriber.next(event);

                    if (event.event === 'complete') {
                      subscriber.complete();
                    }
                  } catch (e) {
                    subscriber.error(e);
                  }
                });

                readStream();
              })
              .catch((err) => subscriber.error(err));
          };

          readStream();
        })
        .catch((err) => subscriber.error(err));
    });
  }

  /** Headers estándar, igual que el interceptor */
  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'X-API-Key': environment.apiKey,
      'Content-Type': 'application/json',
    };

    const token = this.authService.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }
}
