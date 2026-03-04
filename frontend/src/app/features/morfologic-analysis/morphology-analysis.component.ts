import { Component, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { MorphologyAnalysisService } from '@services/body-analysis.service';
import { CartService } from '@services/cart.service';
import { QuickAddModalComponent } from '../../shared/components/quick-add/quick-add.component';
import { AnalisisMorfologico, ProductoRecomendado, TIPOS_CUERPO } from '@models/body_analysis';
import { QuickAddData, QuickAddResult } from '@models/quick_add';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamUpload } from '@ng-icons/jam-icons';
type EstadoAnalisis = 'inicial' | 'cargando' | 'resultado' | 'error';

@Component({
  selector: 'app-analisis-morfologico',
  standalone: true,
  imports: [CommonModule, QuickAddModalComponent, NgIconComponent],
  providers: [provideIcons({ jamUpload })],
  templateUrl: './morphology-analysis.component.html',
})
export class MorphologyAnalysisComponent {
  private analisisService = inject(MorphologyAnalysisService);
  private cartService = inject(CartService);
  private router = inject(Router);


  estado = signal<EstadoAnalisis>('inicial');
  imagenSeleccionada = signal<File | null>(null);
  imagenPreview = signal<string | null>(null);
  resultado = signal<AnalisisMorfologico | null>(null);
  mensajeError = signal<string>('');
  porcentajeProgreso = signal<number>(0);

  // Quick Add Modal
  modalAbierto = signal(false);
  productoParaAgregar = signal<QuickAddData | null>(null);

  // Computed signals
  estaCargando = computed(() => this.estado() === 'cargando');
  tieneResultado = computed(() => this.estado() === 'resultado');
  tieneError = computed(() => this.estado() === 'error');

  tipoCuerpoInfo = computed(() => {
    const tipo = this.resultado()?.tipo_cuerpo;
    return tipo ? TIPOS_CUERPO[tipo] : null;
  });

  // Drag & Drop
  isDragging = signal(false);

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.procesarArchivo(files[0]);
    }
  }

  // File input change
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.procesarArchivo(input.files[0]);
    }
  }

  // Procesar archivo seleccionado
  private procesarArchivo(file: File): void {
    // Validar que sea imagen
    if (!file.type.startsWith('image/')) {
      this.mensajeError.set('Por favor selecciona una imagen válida (JPG, PNG, etc.)');
      this.estado.set('error');
      return;
    }

    // Validar tamaño (máx 10MB)
    if (file.size > 10 * 1024 * 1024) {
      this.mensajeError.set('La imagen es demasiado grande. Máximo 10MB.');
      this.estado.set('error');
      return;
    }

    this.imagenSeleccionada.set(file);
    this.crearPreview(file);
    this.estado.set('inicial');
    this.mensajeError.set('');
  }

  // Crear preview de la imagen
  private crearPreview(file: File): void {
    const reader = new FileReader();
    reader.onload = (e) => {
      this.imagenPreview.set(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  }

  // Analizar imagen
  analizarImagen(): void {
    const imagen = this.imagenSeleccionada();

    if (!imagen) {
      this.mensajeError.set('Por favor selecciona una imagen primero');
      this.estado.set('error');
      return;
    }

    this.estado.set('cargando');
    this.porcentajeProgreso.set(0);
    this.mensajeError.set('');

    // Simular progreso
    const intervalo = setInterval(() => {
      const progreso = this.porcentajeProgreso();
      if (progreso < 90) {
        this.porcentajeProgreso.set(progreso + 10);
      }
    }, 300);

    this.analisisService.analizarImagen(imagen).subscribe({
      next: (resultado) => {
        clearInterval(intervalo);
        this.porcentajeProgreso.set(100);

        setTimeout(() => {
          this.resultado.set(resultado);
          this.estado.set('resultado');

          // Scroll suave a resultados
          setTimeout(() => {
            document.getElementById('resultados')?.scrollIntoView({
              behavior: 'smooth',
              block: 'start',
            });
          }, 100);
        }, 500);
      },
      error: (error: HttpErrorResponse) => {
        clearInterval(intervalo);
        console.error('Error en análisis:', error);

        let mensaje = 'Ocurrió un error al analizar la imagen.';

        if (error.status === 400) {
          mensaje = 'La imagen no es válida o no se pudo procesar.';
        } else if (error.status === 401) {
          mensaje = 'Debes iniciar sesión para usar esta función.';
        } else if (error.status === 500) {
          mensaje = 'Error en el servidor. Por favor intenta de nuevo.';
        } else if (error.error?.detail) {
          mensaje = error.error.detail;
        }

        this.mensajeError.set(mensaje);
        this.estado.set('error');
        this.porcentajeProgreso.set(0);
      },
    });
  }

  // Reiniciar análisis
  nuevoAnalisis(): void {
    this.estado.set('inicial');
    this.imagenSeleccionada.set(null);
    this.imagenPreview.set(null);
    this.resultado.set(null);
    this.mensajeError.set('');
    this.porcentajeProgreso.set(0);
  }

  // Regenerar recomendaciones
  regenerarRecomendaciones(): void {
    const analisisId = this.resultado()?.analisis_id;

    if (!analisisId) return;

    this.estado.set('cargando');
    this.porcentajeProgreso.set(0);

    const intervalo = setInterval(() => {
      const progreso = this.porcentajeProgreso();
      if (progreso < 90) {
        this.porcentajeProgreso.set(progreso + 15);
      }
    }, 200);

    this.analisisService.regenerarRecomendaciones(analisisId).subscribe({
      next: (resultado) => {
        clearInterval(intervalo);
        this.porcentajeProgreso.set(100);

        setTimeout(() => {
          this.resultado.set(resultado);
          this.estado.set('resultado');
        }, 300);
      },
      error: (error) => {
        clearInterval(intervalo);
        console.error('Error regenerando:', error);
        this.mensajeError.set('Error al regenerar recomendaciones');
        this.estado.set('error');
      },
    });
  }

  // Navegar a producto
  verProducto(producto: ProductoRecomendado): void {
    // Registrar interacción de click
    this.analisisService
      .registrarInteraccion({
        recomendacion_id: producto.id,
        tipo_interaccion: 'click',
      })
      .subscribe({
        error: (err) => console.warn('No se pudo registrar interacción:', err),
      });

    // Navegar a detalle del producto
    this.router.navigate(['/productos', producto.id]);
  }

  // Abrir modal de quick add
  agregarAlCarrito(producto: ProductoRecomendado, event: Event): void {
    event.stopPropagation();
    console.log('🛒 agregarAlCarrito llamado', producto);

    this.analisisService.obtenerVariantesProducto(producto.id).subscribe({
      next: (variantes) => {
        console.log('✅ Variantes obtenidas:', variantes);
        this.productoParaAgregar.set(variantes);
        this.modalAbierto.set(true);
      },
      error: (error) => {
        console.error('❌ Error obteniendo variantes:', error);

        // Fallback con datos de prueba
        const quickAddData: QuickAddData = {
          producto_id: producto.id,
          nombre: producto.nombre,
          imagen: producto.imagen_principal || '',
          precio: producto.precio_regular,
          precio_descuento: producto.precio_descuento || '0',
          tallas_disponibles: [{ id: 'default', nombre: 'Única', stock: 10 }],
          colores_disponibles: [{ id: 'default', nombre: 'Original', codigo_hex: '#cccccc' }],
        };

        console.log('📦 Usando fallback:', quickAddData);
        this.productoParaAgregar.set(quickAddData);
        this.modalAbierto.set(true);
      },
    });
  }

  onAddToCart(resultado: QuickAddResult): void {
    // Registrar interacción
    this.analisisService
      .registrarInteraccion({
        recomendacion_id: resultado.producto_id,
        tipo_interaccion: 'agregar_carrito',
      })
      .subscribe({
        error: (err) => console.warn('No se pudo registrar interacción:', err),
      });

    // Agregar al carrito
    this.cartService
      .addItem({
        producto_id: resultado.producto_id,
        talla_id: resultado.talla_id,
        color_id: resultado.color_id,
        cantidad: resultado.cantidad,
      })
      .subscribe({
        next: () => {
          const producto = this.productoParaAgregar();
          this.mostrarNotificacion(`✓ ${producto?.nombre} agregado al carrito`);
        },
        error: (error) => {
          console.error('Error agregando al carrito:', error);

          let mensaje = 'No se pudo agregar al carrito';
          if (error.error?.detail) {
            mensaje = error.error.detail;
          }

          this.mostrarNotificacion(`✗ ${mensaje}`, 'error');
        },
      });
  }

  // Cerrar modal
  onCloseModal(): void {
    this.modalAbierto.set(false);
    this.productoParaAgregar.set(null);
  }

  // Mostrar notificación temporal
  private mostrarNotificacion(mensaje: string, tipo: 'success' | 'error' = 'success'): void {
    // Implementación simple con alert (mejorar con toast/snackbar)
    const icono = tipo === 'success' ? '✓' : '✗';
    const color = tipo === 'success' ? '#10b981' : '#ef4444';

    // Crear elemento de notificación
    const notif = document.createElement('div');
    notif.textContent = mensaje;
    notif.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: ${color};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 9999;
      font-size: 14px;
      animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notif);

    setTimeout(() => {
      notif.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => notif.remove(), 300);
    }, 3000);
  }

  formatearPrecio(precio: string): string {
    return `$${Number(precio).toFixed(2)}`;
  }

  obtenerNivelConfianza(confianza: number): { texto: string; color: string } {
    if (confianza >= 0.9) {
      return { texto: 'Muy alta', color: 'text-green-600' };
    } else if (confianza >= 0.75) {
      return { texto: 'Alta', color: 'text-blue-600' };
    } else if (confianza >= 0.6) {
      return { texto: 'Media', color: 'text-yellow-600' };
    } else {
      return { texto: 'Baja', color: 'text-orange-600' };
    }
  }

  getDiscountPercent(descuento: string, regular: string): number {
    const descuentoNum = parseFloat(descuento);
    const regularNum = parseFloat(regular);

    return ((regularNum - descuentoNum) / regularNum) * 100;
  }
}
