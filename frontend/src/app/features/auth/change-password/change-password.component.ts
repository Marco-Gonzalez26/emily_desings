import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamShield, jamCheck, jamClose } from '@ng-icons/jam-icons';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NgIconComponent, ToastModule],
  providers: [MessageService],
  viewProviders: [provideIcons({ jamShield, jamCheck, jamClose })],
  templateUrl: './change-password.component.html',
  styleUrl: './change-password.component.css',
})
export class ChangePasswordComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  isSubmitting = signal(false);
  showPasswordActual = signal(false);
  showPasswordNueva = signal(false);
  showPasswordConfirmacion = signal(false);

  form: FormGroup;

  constructor() {
    this.form = this.fb.group(
      {
        email: ['', [Validators.required, Validators.email]],
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

  onSubmit(): void {
    if (this.form.invalid || this.isSubmitting()) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);

    this.authService.changePassword(this.form.value).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Éxito',
          detail: 'Contraseña actualizada correctamente',
        });

        setTimeout(() => {
          this.router.navigate(['/perfil']);
        }, 2000);
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
}
