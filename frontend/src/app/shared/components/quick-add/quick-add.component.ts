import { Component, signal, computed, output, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuickAddData, QuickAddResult } from '@models/quick_add';

@Component({
  selector: 'app-quick-add-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './quick-add.component.html',
  styleUrl: './quick-add.component.css',
})
export class QuickAddModalComponent {

  producto = input.required<QuickAddData>();
  isOpen = input.required<boolean>();

  
  close = output<void>();
  addToCart = output<QuickAddResult>();


  tallaSeleccionada = signal<string | null>(null);
  colorSeleccionado = signal<string | null>(null);
  cantidad = signal<number>(1);

  tallaInfo = computed(() => {
    const tallaId = this.tallaSeleccionada();
    if (!tallaId) return null;
    return this.producto().tallas_disponibles.find((t) => t.id === tallaId);
  });

  stockDisponible = computed(() => {
    const talla = this.tallaInfo();
    return talla?.stock ?? 0;
  });

  puedeAgregar = computed(() => {
    return (
      this.tallaSeleccionada() !== null &&
      this.colorSeleccionado() !== null &&
      this.cantidad() > 0 &&
      this.cantidad() <= this.stockDisponible()
    );
  });

  precioFinal = computed(() => {
    const descuento = this.producto().precio_descuento;
    const regular = this.producto().precio;


    if (descuento) {
      return parseFloat(descuento);
    }
    return parseFloat(regular);
  });

  totalPrecio = computed(() => {
    return this.precioFinal() * this.cantidad();
  });


  seleccionarTalla(tallaId: string): void {
    this.tallaSeleccionada.set(tallaId);
  }

  seleccionarColor(colorId: string): void {
    this.colorSeleccionado.set(colorId);
  }

  incrementarCantidad(): void {
    if (this.cantidad() < this.stockDisponible()) {
      this.cantidad.update((c) => c + 1);
    }
  }

  decrementarCantidad(): void {
    if (this.cantidad() > 1) {
      this.cantidad.update((c) => c - 1);
    }
  }

  agregarAlCarrito(): void {
    if (!this.puedeAgregar()) return;

    this.addToCart.emit({
      producto_id: this.producto().producto_id,
      talla_id: this.tallaSeleccionada()!,
      color_id: this.colorSeleccionado()!,
      cantidad: this.cantidad(),
    });

    this.cerrar();
  }

  cerrar(): void {

    this.tallaSeleccionada.set(null);
    this.colorSeleccionado.set(null);
    this.cantidad.set(1);

    this.close.emit();
  }

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.cerrar();
    }
  }
}
