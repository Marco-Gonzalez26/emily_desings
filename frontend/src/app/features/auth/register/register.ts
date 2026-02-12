import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamEye, jamEyeClose } from '@ng-icons/jam-icons';
import { AuthService } from '../../../core/services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, NgIconComponent],
  providers: [provideIcons({ jamEye, jamEyeClose })],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  isLoading = false;
  errorMessage = '';
  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    // Crear formulario con validaciones
    this.registerForm = this.fb.group({
      nombre_completo: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      telefono: [''],
      direccion: [''],
      rol: ['cliente'], // Por defecto cliente
    });
  }

  /**
   * Submit del formulario de registro
   */
  onSubmit(): void {
    // Marcar todos los campos como touched para mostrar errores
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const registerData = this.registerForm.value;

    this.authService.register(registerData).subscribe({
      next: (response) => {
        console.log('Registro exitoso:', response);
        this.isLoading = false;

        // Redirigir a productos
        this.router.navigate(['/productos']);
      },
      error: (error) => {
        console.error('Error en registro:', error);
        this.isLoading = false;

        // Mostrar mensaje de error
        if (error.status === 400) {
          this.errorMessage = 'El email ya está registrado';
        } else {
          this.errorMessage = 'Error al crear la cuenta. Intenta nuevamente.';
        }
      },
    });
  }

  /**
   * Alternar visibilidad de contraseña
   */
  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  /**
   * Helpers para validación de formulario
   */
  get nombre_completo() {
    return this.registerForm.get('nombre_completo');
  }

  get email() {
    return this.registerForm.get('email');
  }

  get password() {
    return this.registerForm.get('password');
  }
}
