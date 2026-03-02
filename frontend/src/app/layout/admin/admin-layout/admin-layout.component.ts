import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import {
  jamDashboard,
  jamBox,
  jamShoppingBag,
  jamUsers,
  jamTag,
  jamPicture,
  jamRuler,
  jamGrid,
  jamLogOut,
  jamMenu,
  jamClose,
  jamFiles,
  jamDocument,
} from '@ng-icons/jam-icons';
import { AuthService } from '../../../core/services/auth';

interface MenuItem {
  label: string;
  icon: string;
  route: string;
  badge?: number;
}

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, NgIconComponent],
  providers: [
    provideIcons({
      jamDashboard,
      jamBox,
      jamShoppingBag,
      jamUsers,
      jamTag,
      jamPicture,
      jamRuler,
      jamGrid,
      jamLogOut,
      jamMenu,
      jamClose,
      jamFiles,
      jamDocument,
    }),
  ],
  templateUrl: './admin-layout.component.html',
})
export class AdminLayoutComponent {
  sidebarOpen = signal(false);

  menuItems: MenuItem[] = [
    { label: 'Dashboard', icon: 'jamDashboard', route: '/admin' },
    { label: 'Productos', icon: 'jamBox', route: '/admin/productos' },
    { label: 'Categorías', icon: 'jamGrid', route: '/admin/categorias' },
    { label: 'Marcas', icon: 'jamTag', route: '/admin/marcas' },
    { label: 'Colores', icon: 'jamPicture', route: '/admin/colores' },
    { label: 'Tallas', icon: 'jamRuler', route: '/admin/tallas' },
    { label: 'Inventario', icon: 'jamShoppingBag', route: '/admin/inventario' },
    { label: 'Órdenes', icon: 'jamDocument', route: '/admin/ordenes', badge: 3 },
    { label: 'Usuarios', icon: 'jamUsers', route: '/admin/usuarios' },
    { label: 'Reportes', icon: 'jamFiles', route: '/admin/reportes' },
  ];

  constructor(
    public authService: AuthService,
    private router: Router,
  ) {}

  toggleSidebar(): void {
    this.sidebarOpen.update((v) => !v);
  }

  closeSidebarMobile(): void {
    if (window.innerWidth < 1024) {
      this.sidebarOpen.set(false);
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/iniciar-sesion']);
  }
}
