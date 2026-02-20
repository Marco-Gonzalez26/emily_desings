import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { Inventario } from '../../shared/models/inventory';

@Injectable({
  providedIn: 'root',
})
export class InventarioService {
  constructor(private api: ApiService) {}

  getInventarioByProducto(productoId: string): Observable<Inventario[]> {
    return this.api.get<Inventario[]>(`/api/inventario/producto/${productoId}`);
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
}
