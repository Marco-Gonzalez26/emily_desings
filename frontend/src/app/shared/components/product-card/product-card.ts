import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './product-card.html',
  styleUrls: ['./product-card.css']
})
export class ProductCardComponent {
  @Input() image: string = '';
  @Input() title: string = '';
  @Input() description: string = '';
  @Input() buttonText: string = 'Saber más';
}
