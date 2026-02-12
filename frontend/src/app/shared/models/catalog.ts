export interface Category {
  id: string;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  created_at: string;
}

export interface Brand {
  id: string;
  nombre: string;
  descripcion?: string;
  logo_url?: string;
  activo: boolean;
  fecha_creacion: string;
}
