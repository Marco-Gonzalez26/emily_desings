import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamUser,
  jamShield,
  jamTrash,
  jamCheck,
  jamPencil,
  jamPhone,
  jamMapMarker,
  jamCreditCard,
  jamClose,
  jamShoppingCart,
  jamCamera,
} from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

import { ProfileService } from '@app/core/services/user_profile.service';
import { AuthService } from '@core/services/auth.service';
import { User } from '@shared/models/user';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NgIconComponent, ToastModule, RouterLink],
  providers: [MessageService],
  viewProviders: [
    provideIcons({
      jamUser,
      jamShield,
      jamTrash,
      jamCheck,
      jamPencil,
      jamPhone,
      jamMapMarker,
      jamCreditCard,
      jamClose,
      jamShoppingCart,
      jamCamera,
    }),
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css',
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private profileService = inject(ProfileService);
  private authService = inject(AuthService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  user = signal<User | null>(null);
  statistics = signal<any>(null);
  isLoading = signal(true);
  isEditMode = signal(false);
  isChangingPassword = signal(false);
  isSubmitting = signal(false);

  profileForm: FormGroup;
  passwordForm: FormGroup;

  showPasswordActual = signal(false);
  showPasswordNueva = signal(false);
  showPasswordConfirmacion = signal(false);

  userInitials = computed(() => {
    const user = this.user();
    if (!user?.nombre_completo) return 'U';
    const names = user.nombre_completo.split(' ');
    return names.length > 1
      ? `${names[0][0]}${names[1][0]}`.toUpperCase()
      : names[0][0].toUpperCase();
  });

  constructor() {
    this.profileForm = this.fb.group({
      nombre_completo: ['', [Validators.required, Validators.minLength(2)]],
      telefono: ['', [Validators.pattern(/^[0-9]{10}$/)]],
      direccion: [''],
      cedula_ruc: ['', [Validators.pattern(/^[0-9]{10,13}$/)]],
    });

    this.passwordForm = this.fb.group(
      {
        password_actual: ['', Validators.required],
        password_nueva: ['', [Validators.required, Validators.minLength(6)]],
        password_confirmacion: ['', Validators.required],
      },
      {
        validators: this.passwordsMatchValidator,
      },
    );
  }

  passwordsMatchValidator(group: FormGroup) {
    const nueva = group.get('password_nueva')?.value;
    const confirmacion = group.get('password_confirmacion')?.value;
    return nueva === confirmacion ? null : { passwordsMismatch: true };
  }

  ngOnInit(): void {
    this.loadProfile();
    this.loadStatistics();
  }

  loadProfile(): void {
    this.isLoading.set(true);

    this.profileService.getProfile().subscribe({
      next: (user) => {
        this.user.set(user);
        this.profileForm.patchValue({
          nombre_completo: user.nombre_completo || '',
          telefono: user.telefono || '',
          direccion: user.direccion || '',
          cedula_ruc: user.cedula_ruc || '',
        });
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error cargando perfil:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo cargar el perfil',
        });
        this.isLoading.set(false);
      },
    });
  }

  loadStatistics(): void {
    this.profileService.getStatistics().subscribe({
      next: (stats) => {
        this.statistics.set(stats);
      },
      error: (error) => {
        console.error('Error cargando estadísticas:', error);
      },
    });
  }

  enableEditMode(): void {
    this.isEditMode.set(true);
  }

  cancelEdit(): void {
    this.isEditMode.set(false);
    const user = this.user();
    if (user) {
      this.profileForm.patchValue({
        nombre_completo: user.nombre_completo || '',
        telefono: user.telefono || '',
        direccion: user.direccion || '',
        cedula_ruc: user.cedula_ruc || '',
      });
    }
  }

  onSubmitProfile(): void {
    if (this.profileForm.invalid || this.isSubmitting()) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);

    this.profileService.updateProfile(this.profileForm.value).subscribe({
      next: (user) => {
        this.user.set(user);
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Perfil actualizado correctamente',
        });
        this.isEditMode.set(false);
        this.isSubmitting.set(false);
      },
      error: (error) => {
        console.error('Error:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'No se pudo actualizar el perfil',
        });
        this.isSubmitting.set(false);
      },
    });
  }

  togglePasswordChange(): void {
    this.isChangingPassword.update((v) => !v);
    if (!this.isChangingPassword()) {
      this.passwordForm.reset();
    }
  }

  onSubmitPassword(): void {
    if (this.passwordForm.invalid || this.isSubmitting()) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);

    this.profileService.changePassword(this.passwordForm.value).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Contraseña actualizada correctamente',
        });
        this.passwordForm.reset();
        this.isChangingPassword.set(false);
        this.isSubmitting.set(false);
      },
      error: (error) => {
        console.error('Error:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.detail || 'No se pudo cambiar la contraseña',
        });
        this.isSubmitting.set(false);
      },
    });
  }



  togglePasswordVisibility(field: 'actual' | 'nueva' | 'confirmacion'): void {
    if (field === 'actual') {
      this.showPasswordActual.update((v) => !v);
    } else if (field === 'nueva') {
      this.showPasswordNueva.update((v) => !v);
    } else {
      this.showPasswordConfirmacion.update((v) => !v);
    }
  }

  formatDate(date: string): string {
    if (!date) return 'No especificado';
    return new Date(date).toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-EC', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  }

  getRolBadge(rol: string): string {
    return rol === 'administrador' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800';
  }

  getRolLabel(rol: string): string {
    return rol === 'administrador' ? 'Administrador' : 'Cliente';
  }
}
