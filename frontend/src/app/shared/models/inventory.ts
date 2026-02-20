import { Color } from './color';
import { Talla } from './size';

export interface Inventario {
  id: string;
  producto_id: string;
  talla_id: string;
  color_id: string;
  stock: number;
  stock_reservado: number;
  talla?: Talla;
  color?: Color;
}
