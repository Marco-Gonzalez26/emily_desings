import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamClose, jamCheck, jamArrowLeft } from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

import { TallaService } from './../../../../core/services/size.service';

import { Talla } from '@app/shared/models/size';

@Component({
  selector: 'app-admin-size-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NgIconComponent, ToastModule],
  providers: [MessageService],
  viewProviders: [provideIcons({ jamClose, jamCheck, jamArrowLeft })],
  templateUrl: './admin-size-form.component.html',
  styleUrl: './admin-size-form.component.css',
})
export class AdminSizeFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private location = inject(Location);
  private sizeService = inject(TallaService);
  private messageService = inject(MessageService);

  form: FormGroup;
  isEditMode = signal(false);
  isLoading = signal(false);
  isSubmitting = signal(false);
  sizeId = signal<string | null>(null);
  nextOrden = signal(1);

  constructor() {
    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(50)]],
      orden: [1, [Validators.required, Validators.min(1)]],
      activo: [true],
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');

    if (id) {
      this.sizeId.set(id);
      this.isEditMode.set(true);
      this.loadSize(id);
    } else {
      // Calcular siguiente orden automáticamente
      this.loadNextOrden();
    }
  }

  loadNextOrden(): void {
    this.sizeService.getTallas(false).subscribe({
      next: (sizes) => {
        const maxOrden = sizes.length > 0 ? Math.max(...sizes.map((s) => s.orden)) : 0;
        this.nextOrden.set(maxOrden + 1);
        this.form.patchValue({ orden: maxOrden + 1 });
      },
      error: () => {
        this.nextOrden.set(1);
      },
    });
  }

  loadSize(id: string): void {
    this.isLoading.set(true);

    this.sizeService.getTallaById(id).subscribe({
      next: (size) => {
        this.form.patchValue({
          nombre: size.nombre,
          orden: size.orden,
          activo: size.activo,
        });
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error cargando talla:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo cargar la talla',
        });
        this.isLoading.set(false);
        this.goBack();
      },
    });
  }

  onSubmit(): void {
    if (this.form.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    if (this.isEditMode()) {
      this.updateSize();
    } else {
      this.createSize();
    }
  }

  createSize(): void {
    this.sizeService.createTalla(this.form.value).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Talla creada exitosamente',
        });

        setTimeout(() => {
          this.router.navigate(['/admin/tallas']);
        }, 1000);
      },
      error: (error) => {
        console.error('Error creando talla:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'No se pudo crear la talla',
        });
        this.isSubmitting.set(false);
      },
    });
  }

  updateSize(): void {
    const id = this.sizeId();
    if (!id) return;

    this.sizeService.updateTalla(id, this.form.value).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Talla actualizada exitosamente',
        });

        setTimeout(() => {
          this.router.navigate(['/admin/tallas']);
        }, 1000);
      },
      error: (error) => {
        console.error('Error actualizando talla:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'No se pudo actualizar la talla',
        });
        this.isSubmitting.set(false);
      },
    });
  }

  goBack(): void {
    this.location.back();
  }

  cancelar(): void {
    this.router.navigate(['/admin/tallas']);
  }
}
