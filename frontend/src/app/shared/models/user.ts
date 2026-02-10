export interface User {
  id: string;
  email: string;
  nombre_completo?: string;
  telefono?: string;
  direccion?: string;
  rol: 'cliente' | 'administrador';
  activo: boolean;
  fecha_registro: string;
  fecha_ultimo_acceso?: string;
}
