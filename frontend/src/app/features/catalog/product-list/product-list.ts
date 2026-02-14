import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamHeart,
  jamHeartF,
  jamShoppingCart,
  jamChevronLeft,
  jamChevronRight,
} from '@ng-icons/jam-icons';
import { ProductoService } from '../../../core/services/product/product';
import { Product, ProductFilters } from '../../../shared/models/product';
import { FiltersComponent } from '../filters/filters';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, NgIconComponent, FiltersComponent],
  providers: [
    provideIcons({ jamHeart, jamHeartF, jamShoppingCart, jamChevronLeft, jamChevronRight }),
  ],
  templateUrl: './product-list.html',
  styleUrl: './product-list.css',
})
export class ProductListComponent implements OnInit {
  products = signal<Product[]>([]);
  isLoading = signal(true);
  totalProducts = signal(0);
  favorites = signal<Set<string>>(new Set());

  currentPage = signal(1);
  pageSize = signal(12);
  totalPages = computed(() => Math.ceil(this.totalProducts() / this.pageSize()));
  pages = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const pages: (number | string)[] = [];

    if (total <= 5) {
      for (let i = 1; i <= total; i++) pages.push(i);
    } else {
      pages.push(1);
      if (current > 3) pages.push('...');
      for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++)
        pages.push(i);
      if (current < total - 2) pages.push('...');
      pages.push(total);
    }
    return pages;
  });

  activeFilters = signal<Partial<ProductFilters>>({});

  sortOptions = [
    { label: 'Recomendado', value: '' },
    { label: 'Menor precio', value: 'precio_asc' },
    { label: 'Mayor precio', value: 'precio_desc' },
    { label: 'Más nuevos', value: 'nuevos' },
  ];
  selectedSort = signal('');

  constructor(private productoService: ProductoService) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.isLoading.set(true);

    const filters: ProductFilters = {
      ...this.activeFilters(),
      activo: true,
      skip: (this.currentPage() - 1) * this.pageSize(),
      limit: this.pageSize(),
    };

    this.productoService.getProducts(filters).subscribe({
      next: (response) => {
        this.products.set(response.productos);
        this.totalProducts.set(response.total);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error al cargar productos:', error);
        this.isLoading.set(false);
      },
    });
  }

  onFiltersChanged(filters: Partial<ProductFilters>): void {
    this.activeFilters.set(filters);
    this.currentPage.set(1);
    this.loadProducts();
  }

  onFiltersCleared(): void {
    this.activeFilters.set({});
    this.currentPage.set(1);
    this.selectedSort.set('');
    this.loadProducts();
  }

  goToPage(page: number | string): void {
    if (typeof page === 'number' && page !== this.currentPage()) {
      this.currentPage.set(page);
      this.loadProducts();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  prevPage(): void {
    if (this.currentPage() > 1) {
      this.currentPage.set(this.currentPage() - 1);
      this.loadProducts();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.set(this.currentPage() + 1);
      this.loadProducts();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  onSortChange(sort: string): void {
    this.selectedSort.set(sort);

    if (sort === '') {
      this.loadProducts();
      return;
    }

    const sorted = [...this.products()];

    switch (sort) {
      case 'precio_asc':
        sorted.sort((a, b) => this.getPrice(a) - this.getPrice(b));
        break;
      case 'precio_desc':
        sorted.sort((a, b) => this.getPrice(b) - this.getPrice(a));
        break;
      case 'nuevos':
        sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
    }

    this.products.set(sorted);
  }

  toggleFavorite(productId: string, event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    const favs = new Set(this.favorites());
    favs.has(productId) ? favs.delete(productId) : favs.add(productId);
    this.favorites.set(favs);
  }

  isFavorite(productId: string): boolean {
    return this.favorites().has(productId);
  }

  addToCart(product: Product, event: Event): void {
    event.stopPropagation();
    event.preventDefault();
    console.log('Agregar al carrito:', product.nombre);
  }

  getMainImage(product: Product): string {
    const main = product.imagenes?.find((img) => img.es_principal);
    return main?.url_imagen ?? product.imagenes?.[0]?.url_imagen ?? 'assets/images/placeholder.jpg';
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
}
