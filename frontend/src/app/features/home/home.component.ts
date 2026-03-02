import {
  Component,
  signal,
  AfterViewInit,
  ElementRef,
  ViewChild,
  PLATFORM_ID,
  Inject,
  OnInit,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { HomeProductCardComponent } from './../../shared/components/home/home-product-card/home-product-card.component';
import { HomeService } from '../../core/services/home.service';
import { Product } from '../../shared/models/product';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { RouterLink } from '@angular/router';

interface Card {
  image: string;
  title: string;
  description: string;
  buttonText: string;
  link?: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, HomeProductCardComponent, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent implements OnInit, AfterViewInit {
  @ViewChild('cardsContainer1') cardsContainer1!: ElementRef;
  @ViewChild('cardsWrapper1') cardsWrapper1!: ElementRef;
  @ViewChild('cardsContainer2') cardsContainer2!: ElementRef;
  @ViewChild('cardsWrapper2') cardsWrapper2!: ElementRef;
  @ViewChild('ctaSection') ctaSection!: ElementRef;
  @ViewChild('finalCTA') finalCTA!: ElementRef;

  // Cards estáticas para primera sección
  protected readonly cards1 = signal<Card[]>([
    {
      image: '/analisis-morfologico.jpeg',
      title: 'Análisis Morfológico',
      description: 'Descubre las prendas perfectas que resaltan tu silueta y personalidad.',
      buttonText: 'Comenzar',
      link: '/analisis-morfologico',
    },
    {
      image: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800',
      title: 'Nuevas Llegadas',
      description: 'Explora nuestras últimas incorporaciones de moda.',
      buttonText: 'Ver Todo',
      link: '/catalogo?es_nuevo=true',
    },
    {
      image: 'https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=800',
      title: 'Ofertas Especiales',
      description: 'Descuentos exclusivos en prendas seleccionadas.',
      buttonText: 'Ver Ofertas',
      link: '/catalogo?es_oferta=true',
    },
    {
      image: '/Emi_ModaLos80.jpeg',
      title: 'Hecho en Quevedo',
      description: 'Moda sostenible con prácticas éticas y artesanos locales.',
      buttonText: 'Conocer Más',
      link: '/sobre-nosotros',
    },
  ]);

  // Productos destacados para segunda sección
  protected readonly productosDestacados = signal<Product[]>([]);

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private homeService: HomeService,
  ) {
    if (isPlatformBrowser(this.platformId)) {
      gsap.registerPlugin(ScrollTrigger);
    }
  }

  ngOnInit(): void {
    // Cargar datos de la home
    this.homeService.getHomeData(8).subscribe({
      next: (data) => {
        this.productosDestacados.set(data.destacados);

        // Inicializar scroll horizontal de productos después de cargar datos
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => {
            this.initSecondScrollAnimation();
          }, 100);
        }
      },
      error: (error) => {
        console.error('Error cargando datos de home:', error);
      },
    });
  }

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => {
        this.initAnimations();
      }, 100);
    }
  }

  getProductImage(product: Product): string {
    const main = product.imagenes?.find((img) => img.es_principal);
    return main?.url_imagen || product.imagenes?.[0]?.url_imagen || 'assets/images/placeholder.jpg';
  }

  getProductPrice(product: Product): number {
    const price = product.precio_descuento || product.precio_regular;
    return parseFloat(price as any) || 0;
  }

  private initAnimations(): void {
    // Animación del hero
    gsap
      .timeline()
      .from('.hero-title', { y: 50, opacity: 0, duration: 1, ease: 'power3.out' })
      .from('.hero-subtitle', { y: 30, opacity: 0, duration: 0.8, ease: 'power3.out' }, '-=0.6')
      .from('.hero-button', { y: 20, opacity: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4');

    // Primer scroll horizontal (datos estáticos)
    this.createHorizontalScroll(
      this.cardsContainer1.nativeElement,
      this.cardsWrapper1.nativeElement,
      false,
    );

    // Animación del CTA intermedio
    this.initCTAAnimation();

    // Animación del CTA final
    this.initFinalCTAAnimation();
  }

  private initSecondScrollAnimation(): void {
    // Segundo scroll horizontal (datos asíncronos)
    if (this.cardsContainer2 && this.cardsWrapper2) {
      this.createHorizontalScroll(
        this.cardsContainer2.nativeElement,
        this.cardsWrapper2.nativeElement,
        true,
      );
    }
  }

  private createHorizontalScroll(
    container: HTMLElement,
    wrapper: HTMLElement,
    reverse: boolean,
  ): void {
    const getScrollAmount = () => {
      const cardsWidth = wrapper.scrollWidth;
      return reverse ? cardsWidth - window.innerWidth : -(cardsWidth - window.innerWidth);
    };

    if (reverse) {
      gsap.set(wrapper, { x: -(wrapper.scrollWidth - window.innerWidth) });
    }

    const tween = gsap.to(wrapper, {
      x: reverse ? 0 : getScrollAmount,
      duration: 3,
      ease: 'none',
    });

    ScrollTrigger.create({
      trigger: container,
      start: 'center center',
      end: () => `+=${Math.abs(getScrollAmount())}`,
      pin: true,
      animation: tween,
      scrub: 1.5,
      invalidateOnRefresh: true,
    });
  }

  private initCTAAnimation(): void {
    const section = this.ctaSection.nativeElement;
    const title = section.querySelector('.cta-title');
    const subtitle = section.querySelector('.cta-subtitle');
    const button = section.querySelector('.cta-button');

    const timeline = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: 'top 70%',
        end: 'bottom 30%',
        toggleActions: 'play none none reverse',
      },
    });

    timeline
      .from(title, { y: 60, opacity: 0, duration: 0.8, ease: 'power3.out' })
      .from(subtitle, { y: 40, opacity: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4')
      .from(button, {
        y: 30,
        scale: 0.85,
        duration: 0.5,
        ease: 'power3.out',
      });
  }

  private initFinalCTAAnimation(): void {
    const section = this.finalCTA.nativeElement;
    const title = section.querySelector('.final-title');
    const subtitle = section.querySelector('.final-subtitle');
    const button = section.querySelector('.final-button');

    const timeline = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: 'top 75%',
        end: 'top 25%',
        toggleActions: 'play none none reverse',
      },
    });

    timeline
      .from(
        title,
        {
          y: 80,
          opacity: 0,
          duration: 0.8,
          ease: 'power3.out',
        },
        '-=0.3',
      )
      .from(
        subtitle,
        {
          y: 50,
          opacity: 0,
          duration: 0.6,
          ease: 'power3.out',
        },
        '-=0.4',
      )
      .from(
        button,
        {
          scale: 0,
          opacity: 0,
          duration: 0.7,
          ease: 'elastic.out(1, 0.5)',
        },
        '-=0.2',
      );
  }
}
