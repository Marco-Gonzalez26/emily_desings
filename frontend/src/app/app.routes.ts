import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { MorphologyAnalysisComponent } from './features/morfologic-analysis/morphology-analysis';
import { AboutUsComponent } from './features/about-us/about-us';
export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'analisis-morfologico', component: MorphologyAnalysisComponent },
  { path: 'sobre-nosotros', component: AboutUsComponent },
  { path: '**', redirectTo: '' },
];
