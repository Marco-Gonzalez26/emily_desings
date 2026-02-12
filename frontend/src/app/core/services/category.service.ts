import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { Category } from '../../shared/models/catalog';

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  constructor(private api: ApiService) {}

  getCategorias(soloActivas: boolean = true): Observable<Category[]> {
    return this.api.get<Category[]>(`/api/categorias/?solo_activas=${soloActivas}`);
  }
}
