import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamArrowLeft,
  jamClock,
  jamCheck,
  jamCog,
  jamArrowCircleDownRight,
  jamClose,
  jamUser,
  jamMapMarker,
  jamCreditCard,
  jamBox,
} from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

import { OrdenService } from '../../../../core/services/order.service';
import { Orden, OrderEstado, OrderEstadoUpdate } from '@app/shared/models/order';

@Component({
  selector: 'app-admin-order-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, NgIconComponent, ToastModule],
  providers: [MessageService],
  viewProviders: [
    provideIcons({
      jamArrowLeft,
      jamClock,
      jamCheck,
      jamCog,
      jamArrowCircleDownRight,
      jamClose,
      jamUser,
      jamMapMarker,
      jamCreditCard,
      jamBox,
    }),
  ],
  templateUrl: './admin-order-detail.component.html',
  styleUrl: './admin-order-detail.component.css',
})
export class AdminOrderDetailComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private location = inject(Location);
  private orderService = inject(OrdenService);
  private messageService = inject(MessageService);

  order = signal<Orden | null>(null);
  isLoading = signal(true);
  isModalOpen = signal(false);
  isSubmitting = signal(false);

  estadoForm: FormGroup;

  estadosDisponibles: OrderEstado[] = [
    'Pendiente',
    'Confirmado',
    'En Proceso',
    'Enviado',
    'Entregado',
    'Cancelado',
  ];

  constructor() {
    this.estadoForm = this.fb.group({
      estado: ['', Validators.required],
      motivo_cancelacion: [''],
    });

    this.estadoForm.get('estado')?.valueChanges.subscribe((estado) => {
      const motivoControl = this.estadoForm.get('motivo_cancelacion');
      if (estado === 'Cancelado') {
        motivoControl?.setValidators([Validators.required]);
      } else {
        motivoControl?.clearValidators();
      }
      motivoControl?.updateValueAndValidity();
    });
  }

  ngOnInit(): void {
    const orderId = this.route.snapshot.paramMap.get('id');

    if (!orderId) {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'ID de orden no válido',
      });
      this.goBack();
      return;
    }

    this.loadOrder(orderId);
  }

  loadOrder(id: string): void {
    this.isLoading.set(true);

    this.orderService.getOrderById(id).subscribe({
      next: (order) => {
        this.order.set(order);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error cargando orden:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo cargar la orden',
        });
        this.isLoading.set(false);
      },
    });
  }

  openEstadoModal(): void {
    const currentOrder = this.order();
    if (!currentOrder) return;

    this.estadoForm.patchValue({
      estado: currentOrder.estado,
      motivo_cancelacion: currentOrder.motivo_cancelacion || '',
    });

    this.isModalOpen.set(true);
  }

  closeEstadoModal(): void {
    this.isModalOpen.set(false);
    this.estadoForm.reset();
  }

  onSubmitEstado(): void {
    if (this.estadoForm.invalid || this.isSubmitting()) {
      this.estadoForm.markAllAsTouched();
      return;
    }

    const currentOrder = this.order();
    if (!currentOrder) return;

    this.isSubmitting.set(true);

    const updateData: OrderEstadoUpdate = {
      estado: this.estadoForm.value.estado,
      motivo_cancelacion: this.estadoForm.value.motivo_cancelacion || undefined,
    };

    this.orderService.updateOrderStatus(currentOrder.id, updateData).subscribe({
      next: (updatedOrder) => {
        this.order.set(updatedOrder);
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Estado actualizado correctamente',
        });
        this.closeEstadoModal();
        this.isSubmitting.set(false);
      },
      error: (error) => {
        console.error('Error actualizando estado:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'No se pudo actualizar el estado',
        });
        this.isSubmitting.set(false);
      },
    });
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
      Enviado: 'jamTruck',
      Entregado: 'jamCheckCircle',
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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  goBack(): void {
    this.location.back();
  }
}
