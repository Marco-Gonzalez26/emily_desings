import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/enviroment';

/**
 * Servicio base para peticiones HTTP a la API
 */
@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * GET request
   */

  // Sobrecarga para blob
  get(endpoint: string, options: { responseType: 'blob' }): Observable<Blob>;

  // Sobrecarga para JSON
  get<T>(
    endpoint: string,
    options?: {
      params?: HttpParams;
      headers?: HttpHeaders;
    },
  ): Observable<T>;

  get<T>(
    endpoint: string,
    options?: {
      params?: HttpParams;
      headers?: HttpHeaders;
      responseType?: 'json' | 'blob';
    },
  ): Observable<T> | Observable<Blob> {
    return this.http.get(`${this.apiUrl}${endpoint}`, {
      headers: options?.headers,
      params: options?.params,
      responseType: (options?.responseType as any) || 'json',
    }) as any;
  }
  /**
   * POST request
   */
  post<T>(endpoint: string, body: any): Observable<T> {
    return this.http.post<T>(`${this.apiUrl}${endpoint}`, body);
  }

  /**
   * PATCH request
   */
  patch<T>(endpoint: string, body: any): Observable<T> {
    return this.http.patch<T>(`${this.apiUrl}${endpoint}`, body);
  }

  /**
   * DELETE request
   */
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.apiUrl}${endpoint}`);
  }

  /**
   * PUT request
   */
  put<T>(endpoint: string, body: any): Observable<T> {
    return this.http.put<T>(`${this.apiUrl}${endpoint}`, body);
  }
}
