import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api';
import { Brand } from '../../shared/models/catalog';

@Injectable({
  providedIn: 'root',
})
export class BrandService {
  constructor(private api: ApiService) {}

  getBrands(soloActivas: boolean = true): Observable<Brand[]> {
    return this.api.get<Brand[]>(`/api/marcas/?solo_activas=${soloActivas}`);
  }
}
