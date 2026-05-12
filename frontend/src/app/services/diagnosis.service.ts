import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface DiagnosisRequest {
  mensaje: string;
  marca?:  string;
  modelo?: string;
}

export interface DiagnosisResponse {
  categoria:      string;
  confianza:      number;
  solucion:       string;
  probabilidades: Record<string, number>;
}

@Injectable({ providedIn: 'root' })
export class DiagnosisService {
  private readonly http    = inject(HttpClient);
  private readonly apiUrl  = '/api/diagnosticar';

  diagnose(request: DiagnosisRequest): Observable<DiagnosisResponse> {
    return this.http
      .post<DiagnosisResponse>(this.apiUrl, request)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    const msg =
      error.status === 0
        ? 'No se pudo conectar con el servidor. Verifica que el backend esté activo.'
        : error.error?.error ?? `Error del servidor (${error.status}).`;
    return throwError(() => new Error(msg));
  }
}
