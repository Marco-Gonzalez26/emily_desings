import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from '../header/header';

@Component({
  selector: 'app-app',
  imports: [RouterOutlet, Header],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class AppLayoutComponent {}
