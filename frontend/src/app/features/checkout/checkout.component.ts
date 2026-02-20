import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamArrowLeft, jamArrowRight, jamCheck } from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { CartService } from '../../core/services/cart.service';
import { OrdenService } from '../../core/services/order.service';
import { OrdenCreate, OrdenItem } from '../../shared/models/order';

@Component({
  selector: 'app-checkout',
  imports: [CommonModule, RouterModule, ReactiveFormsModule, NgIconComponent],
  providers: [provideIcons({ jamArrowLeft, jamArrowRight, jamCheck })],
  templateUrl: './checkout.component.html',
})
export class CheckoutComponent implements OnInit {
  step = signal(1);
  isProcessing = signal(false);
  shippingForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    public cartService: CartService,
    private ordenService: OrdenService,
    private messageService: MessageService,
  ) {}

  ngOnInit(): void {
    this.cartService.getCart().subscribe();

    if (this.cartService.isEmpty()) {
      this.router.navigate(['/carrito']);
      return;
    }

    this.shippingForm = this.fb.group({
      nombre: ['', Validators.required],
      telefono: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
      direccion: ['', Validators.required],
      ciudad: ['', Validators.required],
      provincia: ['', Validators.required],
      codigoPostal: ['', Validators.required],
    });
  }

  get impuestos(): number {
    return Math.round(this.cartService.subtotal() * 0.12 * 100) / 100;
  }

  get total(): number {
    return (
      Math.round((this.cartService.subtotal() + this.impuestos + this.cartService.envio()) * 100) /
      100
    );
  }

  nextStep(): void {
    if (this.step() === 1) {
      if (this.shippingForm.invalid) {
        this.shippingForm.markAllAsTouched();
        this.messageService.add({
          severity: 'warn',
          summary: 'Datos incompletos',
          detail: 'Por favor completa todos los campos requeridos',
        });
        return;
      }
      this.step.set(2);
    }
  }

  prevStep(): void {
    if (this.step() > 1) {
      this.step.update((s) => s - 1);
    }
  }

  procesarPago(): void {
    if (this.shippingForm.invalid) {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Los datos de envío son inválidos',
      });
      return;
    }

    this.isProcessing.set(true);

    const formValues = this.shippingForm.value;
    const direccionCompleta = `${formValues.nombre}, ${formValues.telefono}, ${formValues.direccion}, ${formValues.ciudad}, ${formValues.provincia}, ${formValues.codigoPostal}`;

    const items: OrdenItem[] = this.cartService.items().map((item) => ({
      producto_id: item.producto_id,
      nombre_producto: item.producto?.nombre || 'Producto',
      talla_id: item.talla_id,
      color_id: item.color_id,
      cantidad: item.cantidad,
      precio_unitario: this.cartService.getItemPrice(item),
      subtotal: this.cartService.getItemTotal(item),
    }));

    const ordenData: OrdenCreate = {
      direccion_envio: direccionCompleta,
      subtotal: this.cartService.subtotal(),
      costo_envio: this.cartService.envio(),
      impuestos: this.impuestos,
      total: this.total,
      metodo_pago: 'stripe',
      items: items,
    };

    this.ordenService.crearOrden(ordenData).subscribe({
      next: (orden) => {
        const baseUrl = window.location.origin;
        const checkoutRequest = {
          success_url: `${baseUrl}/checkout/success`,
          cancel_url: `${baseUrl}/checkout/cancel`,
        };

        this.ordenService.crearCheckoutSession(orden.id, checkoutRequest).subscribe({
          next: (response) => {
            window.location.href = response.checkout_url;
          },
          error: () => {
            this.isProcessing.set(false);
            this.messageService.add({
              severity: 'error',
              summary: 'Error',
              detail: 'No se pudo iniciar el proceso de pago',
            });
          },
        });
      },
      error: () => {
        this.isProcessing.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo crear la orden',
        });
      },
    });
  }
}
