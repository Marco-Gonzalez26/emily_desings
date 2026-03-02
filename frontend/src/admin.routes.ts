import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './app/layout/admin/admin-layout/admin-layout.component';
import { AdminDashboardComponent } from './app/features/admin/dashboard/dashboard.component';
import { adminGuard } from './app/core/guards/auth-guard';

export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminLayoutComponent,
    canActivate: [adminGuard],
    children: [
      {
        path: '',
        component: AdminDashboardComponent,
      },
      // TODO: Agregar rutas de CRUDs
      // {
      //   path: 'productos',
      //   loadComponent: () => import('./productos/productos-list.component').then(m => m.ProductosListComponent),
      // },
      // {
      //   path: 'categorias',
      //   loadComponent: () => import('./categorias/categorias-list.component').then(m => m.CategoriasListComponent),
      // },
      // ... más rutas
    ],
  },
];
