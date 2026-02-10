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
  get<T>(endpoint: string, params?: HttpParams): Observable<T> {
    return this.http.get<T>(`${this.apiUrl}${endpoint}`, { params });
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
