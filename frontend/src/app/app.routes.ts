import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { MorphologyAnalysisComponent } from './features/morfologic-analysis/morphology-analysis';
import { AboutUsComponent } from './features/about-us/about-us';
import { LoginComponent } from './features/auth/login/login';
import { AuthLayoutComponent } from './layout/auth/auth';
import { AppLayoutComponent } from './layout/app/app';
import { RegisterComponent } from './features/auth/register/register';
import { ProductListComponent } from './features/catalog/product-list/product-list';
import { ProductDetailComponent } from './features/catalog/product-detail/product-detail';
import { CartComponent } from './features/cart/cart';
import { CheckoutComponent } from './features/checkout/checkout.component';
import { authGuard } from './core/guards/auth-guard';
import { CheckoutCancelComponent } from './features/checkout-cancel/checkout-cancel.component';
import { CheckoutSuccessComponent } from './features/checkout-success/checkout-success.component';
import { OrdersComponent } from './features/orders/orders.component';
import { OrderDetailComponent } from './features/order-detail/order-detail.component';

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
];
