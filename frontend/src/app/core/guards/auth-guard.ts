import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth';

/**
 * Guard de autenticación
 * Protege rutas que requieren usuario autenticado
 */
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Verificar si el usuario está autenticado
  if (authService.isLoggedIn()) {
    return true; // ✅ Permitir acceso
  }

  // ❌ No autenticado - redirigir al login
  // Guardar la URL a la que quería acceder
  router.navigate(['/login'], {
    queryParams: { returnUrl: state.url },
  });

  return false;
};

/**
 * Guard de administrador
 * Protege rutas que requieren permisos de administrador
 */
export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Verificar autenticación
  if (!authService.isLoggedIn()) {
    router.navigate(['/login']);
    return false;
  }

  // Verificar si es administrador
  if (authService.isAdmin()) {
    return true; // ✅ Es admin, permitir acceso
  }

  // ❌ No es admin - redirigir a inicio
  router.navigate(['/']);
  alert('No tienes permisos de administrador para acceder a esta página');

  return false;
};
