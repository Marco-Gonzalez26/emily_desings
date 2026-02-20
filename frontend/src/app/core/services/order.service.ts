import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import {
  Orden,
  OrdenCreate,
  StripeCheckoutRequest,
  StripeCheckoutResponse,
} from '../../shared/models/order';

@Injectable({
  providedIn: 'root',
})
export class OrdenService {
  constructor(private api: ApiService) {}

  crearOrden(data: OrdenCreate): Observable<Orden> {
    return this.api.post<Orden>('/api/ordenes/', data);
  }

  crearCheckoutSession(
    ordenId: string,
    data: StripeCheckoutRequest,
  ): Observable<StripeCheckoutResponse> {
    return this.api.post<StripeCheckoutResponse>(`/api/ordenes/${ordenId}/checkout`, data);
  }

  confirmarPago(sessionId: string): Observable<Orden> {
    return this.api.post<Orden>(`/api/ordenes/confirmar-pago/${sessionId}`, {});
  }

  getMisOrdenes(skip: number = 0, limit: number = 10): Observable<Orden[]> {
    return this.api.get<Orden[]>(`/api/ordenes/mias?skip=${skip}&limit=${limit}`);
  }

  getOrdenById(ordenId: string): Observable<Orden> {
    return this.api.get<Orden>(`/api/ordenes/${ordenId}`);
  }
}
