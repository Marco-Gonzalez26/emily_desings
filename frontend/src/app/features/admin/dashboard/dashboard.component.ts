import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

import { GeneralTabComponent } from './genera-tab/general-tab.component';
import { ProductsTabComponent } from './products-tab/products-tab.component';
import { ClientsTabComponent } from './clients-tab/clients-tab.component';
import { OrdersTabComponent } from './orders-tab/orders-tab.component';
import { AnalysisTabComponent } from './analysis-tab/analysis-tab.component';
import { NgIcon, NgIconComponent, provideIcons } from '@ng-icons/core';
import { jamBox, jamCamera, jamCoin, jamDashboard, jamUsers } from '@ng-icons/jam-icons';

type TabId = 'general' | 'productos' | 'clientes' | 'ventas' | 'analisis';

interface Tab {
  id: TabId;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,

  imports: [
    CommonModule,
    GeneralTabComponent,
    ProductsTabComponent,
    ClientsTabComponent,
    OrdersTabComponent,
    AnalysisTabComponent,

    NgIconComponent,
  ],
  providers: [provideIcons({ jamDashboard, jamBox, jamUsers, jamCoin, jamCamera })],
  templateUrl: './dashboard.component.html',
})
export class AdminDashboardComponent {
  activeTab = signal<TabId>('general');

  tabs: Tab[] = [
    { id: 'general', label: 'General', icon: 'jamDashboard' },
    { id: 'productos', label: 'Productos', icon: 'jamBox' },
    { id: 'clientes', label: 'Clientes', icon: 'jamUsers' },
    { id: 'ventas', label: 'Ventas', icon: 'jamCoin' },
    { id: 'analisis', label: 'Análisis IA', icon: 'jamCamera' },
  ];

  isTabActive = computed(() => (tabId: TabId) => this.activeTab() === tabId);

  selectTab(tabId: TabId): void {
    this.activeTab.set(tabId);
  }
}
