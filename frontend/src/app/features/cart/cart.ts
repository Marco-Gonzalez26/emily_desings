import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamTrash, jamMinus, jamPlus, jamShoppingCart, jamArrowLeft } from '@ng-icons/jam-icons';
import { CartService } from '../../core/services/cart.service';
import { CartItem } from '../../shared/models/cart';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, RouterModule, NgIconComponent],
  providers: [provideIcons({ jamTrash, jamMinus, jamPlus, jamShoppingCart, jamArrowLeft })],
  templateUrl: './cart.html',
})
export class CartComponent implements OnInit {
  isLoading = signal(true);
  updatingItemId = signal<string | null>(null);

  constructor(public cartService: CartService) {}

  ngOnInit(): void {
    this.cartService.getCart().subscribe({
      next: () => this.isLoading.set(false),
      error: () => this.isLoading.set(false),
    });
  }

  increaseQty(item: CartItem): void {
    this.updatingItemId.set(item.id);
    this.cartService.updateItem(item.id, { cantidad: item.cantidad + 1 }).subscribe({
      next: () => this.updatingItemId.set(null),
      error: () => this.updatingItemId.set(null),
    });
  }

  decreaseQty(item: CartItem): void {
    if (item.cantidad <= 1) {
      this.removeItem(item);
      return;
    }
    this.updatingItemId.set(item.id);
    this.cartService.updateItem(item.id, { cantidad: item.cantidad - 1 }).subscribe({
      next: () => this.updatingItemId.set(null),
      error: () => this.updatingItemId.set(null),
    });
  }

  removeItem(item: CartItem): void {
    this.updatingItemId.set(item.id);
    this.cartService.removeItem(item.id).subscribe({
      next: () => this.updatingItemId.set(null),
      error: () => this.updatingItemId.set(null),
    });
  }

  clearCart(): void {
    this.cartService.clearCart().subscribe();
  }

  get impuestos(): number {
    return Math.round(this.cartService.subtotal() * 0.12 * 100) / 100;
  }

  get totalConImpuestos(): number {
    return (
      Math.round((this.cartService.subtotal() + this.impuestos + this.cartService.envio()) * 100) /
      100
    );
  }
}
