import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { MorphologyAnalysisComponent } from './features/morfologic-analysis/morphology-analysis';
import { AboutUsComponent } from './features/about-us/about-us';
import { LoginComponent } from './features/auth/login/login';
import { AuthLayoutComponent } from './layout/auth/auth';
import { AppLayoutComponent } from './layout/app/app';
import { RegisterComponent } from './features/auth/register/register';

export const routes: Routes = [
  {
    path: '',
    component: AppLayoutComponent,
    children: [
      { path: '', component: HomeComponent },
      { path: 'analisis-morfologico', component: MorphologyAnalysisComponent },
      { path: 'sobre-nosotros', component: AboutUsComponent },
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
  }
];
