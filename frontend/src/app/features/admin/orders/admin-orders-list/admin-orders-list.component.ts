import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamSearch,
  jamFilter,
  jamEye,
  jamRefresh,
  jamCalendar,
  jamUser,
  jamBox,
  jamClock,
  jamCheck,
  jamCog,
  jamArrowCircleDownRight,
  jamClose,
} from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

import { OrdenService } from '../../../../core/services/order.service';
import { Orden, OrderEstado, OrderFilters } from '@app/shared/models/order';

@Component({
  selector: 'app-admin-orders-list',
  standalone: true,
  imports: [CommonModule, FormsModule, NgIconComponent, ToastModule],
  providers: [MessageService],
  viewProviders: [
    provideIcons({
      jamSearch,
      jamFilter,
      jamEye,
      jamRefresh,
      jamCalendar,
      jamUser,
      jamBox,
      jamClock,
      jamCheck,
      jamCog,

      jamArrowCircleDownRight,
      jamClose,
    }),
  ],
  templateUrl: './admin-orders-list.component.html',
  styleUrl: './admin-orders-list.component.css',
})
export class AdminOrdersListComponent implements OnInit {
  private orderService = inject(OrdenService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  orders = signal<Orden[]>([]);
  totalOrders = signal(0);

  isLoading = signal(true);
  showFilters = signal(false);

  filters = signal<OrderFilters>({
    skip: 0,
    limit: 50,
  });

  estadosDisponibles: OrderEstado[] = [
    'Pendiente',
    'Confirmado',
    'En Proceso',
    'Enviado',
    'Entregado',
    'Cancelado',
  ];

  readonly Math = Math;
  currentPage = signal(1);
  itemsPerPage = signal(50);

  totalPages = computed(() => {
    return Math.ceil(this.totalOrders() / this.itemsPerPage());
  });

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.isLoading.set(true);

    const currentFilters = {
      ...this.filters(),
      skip: (this.currentPage() - 1) * this.itemsPerPage(),
      limit: this.itemsPerPage(),
    };

    this.orderService.getAllOrders(currentFilters).subscribe({
      next: (response) => {
        this.orders.set(response.ordenes);
        this.totalOrders.set(response.total);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error cargando órdenes:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudieron cargar las órdenes',
        });
        this.isLoading.set(false);
      },
    });
  }

  onFilterChange(): void {
    this.currentPage.set(1);
    this.loadOrders();
  }

  clearFilters(): void {
    this.filters.set({
      skip: 0,
      limit: 50,
    });
    this.currentPage.set(1);
    this.loadOrders();
  }

  toggleFilters(): void {
    this.showFilters.update((v) => !v);
  }

  viewOrderDetail(orderId: string): void {
    this.router.navigate(['/admin/ordenes', orderId]);
  }

  getEstadoColor(estado: OrderEstado): string {
    const colors = {
      Pendiente: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      Confirmado: 'bg-blue-100 text-blue-800 border-blue-200',
      'En Proceso': 'bg-purple-100 text-purple-800 border-purple-200',
      Enviado: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      Entregado: 'bg-green-100 text-green-800 border-green-200',
      Cancelado: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[estado] || 'bg-gray-100 text-gray-800';
  }

  getEstadoIcon(estado: OrderEstado): string {
    const icons = {
      Pendiente: 'jamClock',
      Confirmado: 'jamCheck',
      'En Proceso': 'jamCog',
      Enviado: 'jamArrowCircleDownRight',
      Entregado: 'jamBox',
      Cancelado: 'jamClose',
    };
    return icons[estado] || 'jamBox';
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-EC', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  changePage(page: number): void {
    this.currentPage.set(page);
    this.loadOrders();
  }

  previousPage(): void {
    if (this.currentPage() > 1) {
      this.currentPage.update((p) => p - 1);
      this.loadOrders();
    }
  }

  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.currentPage.update((p) => p + 1);
      this.loadOrders();
    }
  }
}
