import { Product } from './product';

export interface CartItem {
  id: string;
  carrito_id: string;
  producto_id: string;
  talla_id: string;
  color_id: string;
  cantidad: number;
  precio_unitario: number | string;
  producto?: Product;
  created_at: string;
}

export interface Cart {
  id: string;
  usuario_id: string;
  activo: boolean;
  created_at: string;
  items: CartItem[];
}

export interface CartTotal {
  subtotal: number;
  envio: number;
  total: number;
  cantidad_items: number;
}

export interface AddItemRequest {
  producto_id: string;
  talla_id: string;
  color_id: string;
  cantidad: number;
}

export interface UpdateItemRequest {
  cantidad: number;
}
