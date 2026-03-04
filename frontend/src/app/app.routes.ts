import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { MorphologyAnalysisComponent } from './features/morfologic-analysis/morphology-analysis.component';
import { AboutUsComponent } from './features/about-us/about-us';
import { LoginComponent } from './features/auth/login/login';
import { AuthLayoutComponent } from './layout/auth/auth';
import { AppLayoutComponent } from './layout/app/app';
import { RegisterComponent } from './features/auth/register/register';
import { ProductListComponent } from './features/catalog/product-list/product-list';
import { ProductDetailComponent } from './features/catalog/product-detail/product-detail';
import { CartComponent } from './features/cart/cart';
import { CheckoutComponent } from './features/checkout/checkout.component';
import { adminGuard, authGuard } from './core/guards/auth-guard';
import { CheckoutCancelComponent } from './features/checkout-cancel/checkout-cancel.component';
import { CheckoutSuccessComponent } from './features/checkout-success/checkout-success.component';
import { OrdersComponent } from './features/orders/orders.component';
import { OrderDetailComponent } from './features/order-detail/order-detail.component';

import { AdminLayoutComponent } from './layout/admin/admin-layout/admin-layout.component';
import { AdminDashboardComponent } from './features/admin/dashboard/dashboard.component';
import { AdminCategoryFormComponent } from './features/admin/categories/admin-category-form/admin-category-form.component';
import { AdminBrandFormComponent } from './features/admin/brands/admin-brand-form/admin-brand-form.component';
import { AdminColorsListComponent } from './features/admin/colors/admin-colors-list/admin-colors-list.component';
import { AdminColorFormComponent } from './features/admin/colors/admin-color-form/admin-color-form.component';
import { AdminSizesListComponent } from './features/admin/sizes/admin-sizes-list/admin-sizes-list.component';
import { AdminSizeFormComponent } from './features/admin/sizes/admin-size-form/admin-size-form.component';
import { AdminProductsListComponent } from './features/admin/products/admin-products-list/admin-products-list.component';
import { AdminProductFormComponent } from './features/admin/products/admin-product-form/admin-product-form.component';
import { AdminInventoryListComponent } from './features/admin/inventories/admin-inventories-list/admin-inventories-list.component';
import { AdminProductInventoryComponent } from './features/admin/inventories/admin-product-inventory/admin-product-inventory.component';
import { AdminOrdersListComponent } from './features/admin/orders/admin-orders-list/admin-orders-list.component';
import { AdminOrderDetailComponent } from './features/admin/orders/admin-order-detail/admin-order-detail.component';

export const routes: Routes = [
  {
    path: '',
    component: AppLayoutComponent,
    children: [
      { path: '', component: HomeComponent },
      { path: 'analisis-morfologico', component: MorphologyAnalysisComponent },
      { path: 'sobre-nosotros', component: AboutUsComponent },
      { path: 'catalogo', component: ProductListComponent },
      { path: 'productos/:id', component: ProductDetailComponent },
      { path: 'carrito', component: CartComponent },
      { path: 'checkout', component: CheckoutComponent, canActivate: [authGuard] },
      { path: 'checkout/success', component: CheckoutSuccessComponent, canActivate: [authGuard] },
      { path: 'checkout/cancel', component: CheckoutCancelComponent, canActivate: [authGuard] },
      { path: 'ordenes', component: OrdersComponent, canActivate: [authGuard] },
      { path: 'ordenes/:id', component: OrderDetailComponent, canActivate: [authGuard] },
    ],
  },
  {
    path: 'iniciar-sesion',
    component: AuthLayoutComponent,
    children: [{ path: '', component: LoginComponent }],
  },
  {
    path: 'crear-cuenta',
    component: AuthLayoutComponent,
    children: [{ path: '', component: RegisterComponent }],
  },
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [adminGuard],
    canActivateChild: [adminGuard],
    children: [
      {
        path: '',
        component: AdminDashboardComponent,
      },
      {
        path: 'categorias',
        loadComponent: () =>
          import('./features/admin/categories/admin-categories-list/admin-categories-list.component').then(
            (m) => m.AdminCategoriesListComponent,
          ),
      },
      {
        path: 'categorias/nueva',
        component: AdminCategoryFormComponent,
      },
      {
        path: 'categorias/editar/:id',
        component: AdminCategoryFormComponent,
      },
      {
        path: 'marcas',
        loadComponent: () =>
          import('./features/admin/brands/admin-brands-list/admin-brands-list.component').then(
            (m) => m.AdminBrandsListComponent,
          ),
      },
      {
        path: 'marcas/nueva',
        component: AdminBrandFormComponent,
      },
      {
        path: 'marcas/editar/:id',
        component: AdminBrandFormComponent,
      },
      {
        path: 'colores',
        children: [
          { path: '', component: AdminColorsListComponent },
          { path: 'nuevo', component: AdminColorFormComponent },
          { path: 'editar/:id', component: AdminColorFormComponent },
        ],
      },
      {
        path: 'tallas',
        children: [
          { path: '', component: AdminSizesListComponent },
          { path: 'nueva', component: AdminSizeFormComponent },
          { path: 'editar/:id', component: AdminSizeFormComponent },
        ],
      },
      {
        path: 'productos',
        children: [
          { path: '', component: AdminProductsListComponent },
          { path: 'nuevo', component: AdminProductFormComponent },
          { path: 'editar/:id', component: AdminProductFormComponent },
        ],
      },
      {
        path: 'inventario',
        children: [
          {
            path: '',
            component: AdminInventoryListComponent,
          },
          {
            path: 'producto/:id',
            component: AdminProductInventoryComponent,
          },
        ],
      },
      {
        path: 'ordenes',
        children: [
          { path: '', component: AdminOrdersListComponent },
          { path: ':id', component: AdminOrderDetailComponent },
        ],
      },
    ],
  },
];
