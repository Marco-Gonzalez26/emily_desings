export interface User {
  id: string;
  email: string;
  nombre_completo?: string;
  telefono?: string;
  direccion?: string;
  rol: 'cliente' | 'administrador';
  activo: boolean;
  cedula_ruc?: string;
  fecha_registro: string;
  fecha_ultimo_acceso?: string;
}
