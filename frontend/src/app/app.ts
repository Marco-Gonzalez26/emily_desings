import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from './layout/header/header';
import { PrimeNG } from 'primeng/config';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header],

  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  protected readonly title = signal('EmilyDesings | Pagina Principal');

  constructor(private primeNG: PrimeNG) {}

  ngOnInit() {
    this.primeNG.ripple.set(true);
  }
}
