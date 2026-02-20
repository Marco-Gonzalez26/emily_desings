import { Product } from './product';

export interface OrdenItem {
  producto_id: string;
  nombre_producto: string;
  talla_id: string;
  color_id: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;

  producto?: Product;
}

export interface OrdenCreate {
  direccion_envio: string;
  subtotal: number;
  costo_envio: number;
  impuestos: number;
  total: number;
  metodo_pago: string;
  items: OrdenItem[];
}

export interface Orden {
  id: string;
  numero_orden: string;
  usuario_id: string;
  direccion_envio: string;
  subtotal: number;
  costo_envio: number;
  impuestos: number;
  total: number;
  estado: string;
  metodo_pago?: string;
  stripe_payment_id?: string;
  motivo_cancelacion?: string;
  fecha_orden: string;
  fecha_actualizacion_estado?: string;
  created_at: string;
  updated_at: string;
  items: OrdenItem[];
}

export interface StripeCheckoutRequest {
  success_url: string;
  cancel_url: string;
}

export interface StripeCheckoutResponse {
  checkout_url: string;
  session_id: string;
}
