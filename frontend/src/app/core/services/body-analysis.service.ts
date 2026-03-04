import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AnalisisMorfologico } from '@models/body_analysis';
import { QuickAddData } from '@models/quick_add';

@Injectable({
  providedIn: 'root',
})
export class MorphologyAnalysisService {
  constructor(private apiService: ApiService) {}

  /**
   * Analiza una imagen y genera recomendaciones
   */
  analizarImagen(imagen: File, usarSegmentacion: boolean = true): Observable<AnalisisMorfologico> {
    const formData = new FormData();
    formData.append('file', imagen);

    // Construir endpoint con query params si es necesario
    const endpoint = usarSegmentacion
      ? '/api/analisis/analizar-imagen'
      : '/api/analisis/analizar-imagen?usar_segmentacion=false';

    return this.apiService.post<AnalisisMorfologico>(endpoint, formData);
  }

  /**
   * Obtiene el historial de análisis del usuario
   */
  obtenerHistorial(limit: number = 10): Observable<any[]> {
    return this.apiService.get<any[]>(`/api/analisis/historial?limit=${limit}`);
  }

  /**
   * Obtiene un análisis específico por ID
   */
  obtenerAnalisisPorId(analisisId: string): Observable<AnalisisMorfologico> {
    return this.apiService.get<AnalisisMorfologico>(`/api/analisis/historial/${analisisId}`);
  }

  /**
   * Regenera recomendaciones para un análisis existente
   */
  regenerarRecomendaciones(analisisId: string): Observable<AnalisisMorfologico> {
    return this.apiService.post<AnalisisMorfologico>(`/api/analisis/regenerar/${analisisId}`, {});
  }

  /**
   * Registra interacción del usuario con una recomendación
   */
  registrarInteraccion(data: {
    recomendacion_id: string;
    tipo_interaccion: 'click' | 'agregar_carrito' | 'compra';
  }): Observable<any> {
    return this.apiService.post('/api/analisis/interaccion', data);
  }

  /**
   * Obtiene tipos de cuerpo disponibles
   */
  obtenerTiposCuerpo(): Observable<{ tipos: string[] }> {
    return this.apiService.get<{ tipos: string[] }>('/api/analisis/tipos-cuerpo');
  }

  /**
   * Obtiene variantes (tallas/colores) de un producto
   */
  obtenerVariantesProducto(productoId: string): Observable<QuickAddData> {
    return this.apiService.get<QuickAddData>(`/api/productos/${productoId}/variantes`);
  }
}

// Agregar este import al inicio del archivo
