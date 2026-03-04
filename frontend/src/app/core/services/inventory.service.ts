import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  Inventario,
  InventoryAjuste,
  InventoryCreate,
  InventoryFilters,
  InventoryListResponse,
  InventoryUpdate,
  InventoryWithDetails,
  StockBajoResponse,
} from '../../shared/models/inventory';

@Injectable({
  providedIn: 'root',
})
export class InventarioService {
  private api = inject(ApiService);

  // Listar inventario con filtros (admin)
  getInventarios(filters?: InventoryFilters): Observable<InventoryListResponse> {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const queryString = params.toString();
    const url = queryString ? `/api/inventario?${queryString}` : '/api/inventario';

    return this.api.get<InventoryListResponse>(url);
  }

  // Inventario disponible de un producto (público)
  getInventarioProducto(productoId: string): Observable<InventoryWithDetails[]> {
    return this.api.get<InventoryWithDetails[]>(`/api/inventario/producto/${productoId}`);
  }

  // TODO el inventario de un producto (admin - incluye stock 0)
  getAllInventarioProducto(productoId: string): Observable<InventoryWithDetails[]> {
    return this.api.get<InventoryWithDetails[]>(`/api/inventario/producto/${productoId}/all`);
  }

  getStockDisponible(
    productoId: string,
    tallaId: string,
    colorId: string,
  ): Observable<{ stock_disponible: number }> {
    return this.api.get<{ stock_disponible: number }>(
      `/api/inventario/disponible/${productoId}/${tallaId}/${colorId}`,
    );
  }

  getStockBajo(umbral: number = 10): Observable<StockBajoResponse> {
    return this.api.get<StockBajoResponse>(`/api/inventario/stock-bajo?umbral=${umbral}`);
  }

  createInventario(data: InventoryCreate): Observable<Inventario> {
    return this.api.post<Inventario>('/api/inventario', data);
  }

  updateInventario(id: string, data: InventoryUpdate): Observable<Inventario> {
    return this.api.put<Inventario>(`/api/inventario/${id}`, data);
  }

  ajustarStock(id: string, data: InventoryAjuste): Observable<Inventario> {
    return this.api.post<Inventario>(`/api/inventario/${id}/ajustar`, data);
  }

  deleteInventario(id: string): Observable<Inventario> {
    return this.api.delete<Inventario>(`/api/inventario/${id}`);
  }
}
