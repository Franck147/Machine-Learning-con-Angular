import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface DiagnosisRequest {
  mensaje: string;
  contexto?: string[];
  marca?: string;
  serie?: string;
}

export interface DiagnosisResult {
  necesita_mas_info: false;
  categoria: string;
  confianza: number;
  solucion: string;
  probabilidades: Record<string, number>;
  log_id: string | null;
  marca: string | null;
  serie: string | null;
}

export interface ClarificationResult {
  necesita_mas_info: true;
  pregunta: string;
  probabilidades: Record<string, number>;
  confianza_maxima: number;
}

export type DiagnosisResponse = DiagnosisResult | ClarificationResult;

export interface FeedbackRequest {
  log_id:              string;
  util:                boolean;
  comentario?:         string;
  categoria_correcta?: string;
}

@Injectable({ providedIn: 'root' })
export class DiagnosisService {
  private readonly http = inject(HttpClient);

  private readonly apiDiagnosticar = '/api/diagnosticar';
  private readonly apiFeedback     = '/api/feedback';

  diagnose(
    mensaje: string,
    contexto: string[] = [],
    marca?: string,
    serie?: string,
  ): Observable<DiagnosisResponse> {
    const body: DiagnosisRequest = { mensaje };
    if (contexto.length) body.contexto = contexto;
    if (marca)           body.marca    = marca;
    if (serie)           body.serie    = serie;

    return this.http
      .post<DiagnosisResponse>(this.apiDiagnosticar, body)
      .pipe(catchError(this.handleError));
  }

  sendFeedback(
    log_id:             string,
    util:               boolean,
    comentario?:        string,
    categoria_correcta?: string,
  ): Observable<{ ok: boolean }> {
    const body: FeedbackRequest = { log_id, util };
    if (comentario?.trim())        body.comentario         = comentario.trim();
    if (categoria_correcta?.trim()) body.categoria_correcta = categoria_correcta.trim();

    return this.http
      .post<{ ok: boolean }>(this.apiFeedback, body)
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
