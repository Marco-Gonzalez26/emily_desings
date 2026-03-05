import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
       
          localStorage.removeItem('access_token');
          localStorage.removeItem('current_user');
          router.navigate(['/iniciar-sesion']);
          break;

        case 403:

          router.navigate(['/']);
          break;

        case 404:

          router.navigate(['/']);
          break;

        case 500:

          console.error('Error del servidor:', error.message);
          break;
      }

      return throwError(() => error);
    }),
  );
};
