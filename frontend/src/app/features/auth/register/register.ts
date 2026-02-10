import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth';
import { RegisterRequest } from '../../../shared/models/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './register.html',
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
    this.registerForm = this.fb.group({
      nombre_completo: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      telefono: [''],
      direccion: [''],
    });
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const payload: RegisterRequest = {
      ...this.registerForm.value,
      rol: 'cliente',
    };

    this.authService.register(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/iniciar-sesion']);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage =
          error?.error?.message || 'Error al crear la cuenta. Intenta nuevamente.';
      },
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  get f() {
    return this.registerForm.controls;
  }
}
