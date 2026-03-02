export interface AnalisisMorfologico {
  analisis_id: string;
  tipo_cuerpo: string;
  confianza: number;
  fecha_analisis: string;
  recomendaciones: ProductoRecomendado[];
  total_recomendaciones: number;
}

export interface ProductoRecomendado {
  id: string;
  nombre: string;
  descripcion: string;
  precio_regular: string;
  precio_descuento: string | null;
  categoria: string;
  marca: string | null;
  imagen_principal: string;
  razon: string;
  palabras_clave: string[];
  score?: number;
}

export interface TipoCuerpo {
  nombre: string;
  descripcion: string;
  icono?: string;
}

export const TIPOS_CUERPO: Record<string, TipoCuerpo> = {
  'Triangulo Invertido': {
    nombre: 'Triángulo Invertido',
    descripcion: 'Hombros más anchos que las caderas',
  },
  'Reloj de Arena': {
    nombre: 'Reloj de Arena',
    descripcion: 'Hombros y caderas balanceados con cintura definida',
  },
  Rectangulo: {
    nombre: 'Rectángulo',
    descripcion: 'Proporciones equilibradas sin curvas pronunciadas',
  },
  Triangulo: {
    nombre: 'Triángulo',
    descripcion: 'Caderas más anchas que los hombros',
  },
  Ovalo: {
    nombre: 'Óvalo',
    descripcion: 'Cintura menos definida con curvas suaves',
  },
};
