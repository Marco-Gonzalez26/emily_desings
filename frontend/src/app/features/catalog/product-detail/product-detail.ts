import { ToastModule } from 'primeng/toast';
import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamHeart,
  jamHeartF,
  jamShoppingCart,
  jamChevronLeft,
  jamChevronRight,
  jamShield,
  jamUndo,
  jamStar,
  jamStarF,
  jamMinus,
  jamPlus,
} from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { Product } from '../../../shared/models/product';
import { Inventario } from '../../../shared/models/inventory';
import { CartService } from '../../../core/services/cart.service';
import { InventarioService } from '../../../core/services/inventory.service';
import { ProductoService } from '../../../core/services/product.service';
import { Talla } from '../../../shared/models/size';
import { Color } from '../../../shared/models/color';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, NgIconComponent, ToastModule],
  providers: [
    MessageService,
    provideIcons({
      jamHeart,
      jamHeartF,
      jamShoppingCart,
      jamChevronLeft,
      jamChevronRight,
      jamShield,

      jamUndo,
      jamStar,
      jamStarF,
      jamMinus,
      jamPlus,
    }),
  ],
  templateUrl: './product-detail.html',
  styleUrl: './product-detail.css',
})
export class ProductDetailComponent implements OnInit {
  product = signal<Product | null>(null);
  relatedProducts = signal<Product[]>([]);
  inventario = signal<Inventario[]>([]);
  isLoading = signal(true);
  isFavorite = signal(false);

  tallasDisponibles = computed(() => {
    const uniqueTallas = new Map<string, Talla>();
    this.inventario().forEach((inv) => {
      if (inv.talla) uniqueTallas.set(inv.talla.id, inv.talla);
    });
    return Array.from(uniqueTallas.values()).sort((a, b) => a.orden - b.orden);
  });

  coloresDisponibles = computed(() => {
    const uniqueColores = new Map<string, Color>();
    this.inventario().forEach((inv) => {
      if (inv.color) uniqueColores.set(inv.color.id, inv.color);
    });
    console.log({ uniqueColores });
    return Array.from(uniqueColores.values());
  });

  selectedImageIndex = signal(0);
  selectedImage = computed(() => {
    const imgs = this.product()?.imagenes;
    if (!imgs || imgs.length === 0) return 'assets/images/placeholder.jpg';
    return imgs[this.selectedImageIndex()]?.url_imagen ?? 'assets/images/placeholder.jpg';
  });

  selectedTalla = signal<string | null>(null);
  selectedColor = signal<Color | null>(null);
  quantity = signal(1);
  stockDisponible = signal<number>(0);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productoService: ProductoService,
    private cartService: CartService,
    private inventarioService: InventarioService,
    private messageService: MessageService,
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = params['id'];
      if (id) {
        this.loadProduct(id);
      }
    });
  }

  loadProduct(id: string): void {
    this.isLoading.set(true);
    this.selectedImageIndex.set(0);

    this.productoService.getProductById(id).subscribe({
      next: (product) => {
        this.product.set(product);
        this.loadInventario(id);
        this.loadRelated(product);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
        this.router.navigate(['/productos']);
      },
    });
  }

  loadInventario(productoId: string): void {
    this.inventarioService.getInventarioProducto(productoId).subscribe({
      next: (inventario) => this.inventario.set(inventario),
      error: () => console.error('Error cargando inventario'),
    });
  }

  loadRelated(product: Product): void {
    this.productoService
      .getProducts({
        categoria_id: product.categoria_id ?? undefined,
        activo: true,
        limit: 5,
        skip: 0,
      })
      .subscribe({
        next: (response) => {
          const filtered = response.productos.filter((p) => p.id !== product.id).slice(0, 4);
          this.relatedProducts.set(filtered);
        },
        error: () => this.relatedProducts.set([]),
      });
  }

  selectImage(index: number): void {
    this.selectedImageIndex.set(index);
  }

  prevImage(): void {
    const total = this.product()?.imagenes?.length ?? 0;
    if (total === 0) return;
    this.selectedImageIndex.update((i) => (i === 0 ? total - 1 : i - 1));
  }

  nextImage(): void {
    const total = this.product()?.imagenes?.length ?? 0;
    if (total === 0) return;
    this.selectedImageIndex.update((i) => (i === total - 1 ? 0 : i + 1));
  }

  selectTalla(tallaId: string): void {
    this.selectedTalla.set(this.selectedTalla() === tallaId ? null : tallaId);
    this.updateStockDisponible();
  }

  selectColor(color: Color): void {
    this.selectedColor.set(this.selectedColor()?.id === color.id ? null : color);
    this.updateStockDisponible();
  }

  updateStockDisponible(): void {
    const product = this.product();
    const talla = this.selectedTalla();
    const color = this.selectedColor();

    if (!product || !talla || !color) {
      this.stockDisponible.set(0);
      return;
    }

    this.inventarioService.getStockDisponible(product.id, talla, color.id).subscribe({
      next: (response) => this.stockDisponible.set(response.stock_disponible),
      error: () => this.stockDisponible.set(0),
    });
  }

  getTallaDisplay(talla: Talla): string {
    return talla.nombre;
  }

  decreaseQty(): void {
    if (this.quantity() > 1) this.quantity.update((q) => q - 1);
  }

  increaseQty(): void {
    const maxStock = this.stockDisponible();
    if (this.quantity() < maxStock && this.quantity() < 10) {
      this.quantity.update((q) => q + 1);
    }
  }

  toggleFavorite(): void {
    this.isFavorite.update((v) => !v);
  }

  addToCart(): void {
    const product = this.product();
    if (!product) return;

    if (!this.selectedTalla()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Atención',
        detail: 'Por favor selecciona una talla',
      });
      return;
    }

    if (!this.selectedColor()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Atención',
        detail: 'Por favor selecciona un color',
      });
      return;
    }

    if (this.stockDisponible() < this.quantity()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Stock insuficiente',
        detail: `Solo hay ${this.stockDisponible()} unidades disponibles`,
      });
      return;
    }

    this.cartService
      .addItem({
        producto_id: product.id,
        talla_id: this.selectedTalla()!,
        color_id: this.selectedColor()!.id,
        cantidad: this.quantity(),
      })
      .subscribe({
        next: () => {
          this.messageService.add({
            severity: 'success',
            summary: '¡Listo!',
            detail: 'Producto agregado al carrito',
          });
          this.quantity.set(1);
        },
        error: () =>
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'No se pudo agregar el producto',
          }),
      });
  }

  goBack(): void {
    this.router.navigate(['/productos']);
  }

  getPrice(product: Product): number {
    const price = product.precio_descuento ?? product.precio_regular;
    return parseFloat(price as any) || 0;
  }

  hasDiscount(product: Product): boolean {
    const regular = parseFloat(product.precio_regular as any);
    const descuento = parseFloat(product.precio_descuento as any);
    return !!product.precio_descuento && descuento < regular;
  }

  getDiscountPercent(product: Product): number {
    if (!this.hasDiscount(product)) return 0;
    const regular = parseFloat(product.precio_regular as any);
    const descuento = parseFloat(product.precio_descuento as any);
    return Math.round((1 - descuento / regular) * 100);
  }

  getMainImage(product: Product): string {
    const main = product.imagenes?.find((img) => img.es_principal);
    return main?.url_imagen ?? product.imagenes?.[0]?.url_imagen ?? 'assets/images/placeholder.jpg';
  }
}
