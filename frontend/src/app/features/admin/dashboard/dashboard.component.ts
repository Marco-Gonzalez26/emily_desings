import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamCreditCard, jamShoppingCart, jamBox, jamUsers } from '@ng-icons/jam-icons';

interface KPI {
  label: string;
  value: string;
  icon: string;
  color: string;
  change?: string;
  isPositive?: boolean;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, NgIconComponent],
  providers: [provideIcons({ jamCreditCard, jamShoppingCart, jamBox, jamUsers })],
  templateUrl: './dashboard.component.html',
})
export class AdminDashboardComponent {
  kpis: KPI[] = [
    {
      label: 'Ventas del Mes',
      value: '$0.00',
      icon: 'jamCreditCard',
      color: 'bg-green-500',
      change: '+0% vs mes anterior',
      isPositive: true,
    },
    {
      label: 'Órdenes',
      value: '0',
      icon: 'jamShoppingCart',
      color: 'bg-emily-gold',
      change: '+0 esta semana',
      isPositive: true,
    },
    {
      label: 'Productos',
      value: '0',
      icon: 'jamBox',
      color: 'bg-emily-rose',
    },
    {
      label: 'Usuarios',
      value: '0',
      icon: 'jamUsers',
      color: 'bg-emily-taupe',
    },
  ];
}
