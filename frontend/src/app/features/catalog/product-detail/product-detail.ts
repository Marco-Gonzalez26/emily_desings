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
  jamBox,
  jamUndo,
  jamStar,
  jamStarF,
  jamMinus,
  jamPlus,
} from '@ng-icons/jam-icons';
import { ProductoService } from '../../../core/services/product/product';
import { Product } from '../../../shared/models/product';
import { CartService } from '../../../core/services/cart.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, NgIconComponent],
  providers: [
    provideIcons({
      jamHeart,
      jamHeartF,
      jamShoppingCart,
      jamChevronLeft,
      jamChevronRight,
      jamShield,
      jamBox,
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
  isLoading = signal(true);
  isFavorite = signal(false);

  selectedImageIndex = signal(0);
  selectedImage = computed(() => {
    const imgs = this.product()?.imagenes;
    if (!imgs || imgs.length === 0) return 'assets/images/placeholder.jpg';
    return imgs[this.selectedImageIndex()]?.url_imagen ?? 'assets/images/placeholder.jpg';
  });

  selectedTalla = signal<string | null>(null);
  selectedColor = signal<string | null>(null);
  quantity = signal(1);

  tallas = ['XS', 'S', 'M', 'L', 'XL'];

  // TODO: Obtener colores de la API
  colors = [
    { name: 'Rosa', hex: '#D4A5A5' },
    { name: 'Verde', hex: '#A8B5A0' },
    { name: 'Crema', hex: '#F5EDE3' },
    { name: 'Marrón', hex: '#3E352F' },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productoService: ProductoService,
    private cartService: CartService,
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
        this.isLoading.set(false);
        this.loadRelated(product);
      },
      error: () => {
        this.isLoading.set(false);
        this.router.navigate(['/productos']);
      },
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

  selectTalla(talla: string): void {
    this.selectedTalla.set(this.selectedTalla() === talla ? null : talla);
  }

  selectColor(color: string): void {
    this.selectedColor.set(this.selectedColor() === color ? null : color);
  }

  decreaseQty(): void {
    if (this.quantity() > 1) this.quantity.update((q) => q - 1);
  }

  increaseQty(): void {
    if (this.quantity() < 10) this.quantity.update((q) => q + 1);
  }

  toggleFavorite(): void {
    this.isFavorite.update((v) => !v);
  }

  addToCart(): void {
    if (!this.selectedTalla()) {
      alert('Por favor selecciona una talla');
      return;
    }
    const product = this.product();
    if (!product) return;

    this.cartService
      .addItem({
        producto_id: product.id,
        talla_id: this.selectedTalla()!,
        color_id: this.selectedColor() ?? '',
        cantidad: this.quantity(),
      })
      .subscribe();
  }

  goBack(): void {
    this.router.navigate(['/productos']);
  }

  // Helpers
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
