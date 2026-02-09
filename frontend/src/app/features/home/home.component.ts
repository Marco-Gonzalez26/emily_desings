import {
  Component,
  signal,
  AfterViewInit,
  ElementRef,
  ViewChild,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ProductCardComponent } from '../../shared/components/product-card/product-card';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

interface Card {
  image: string;
  title: string;
  description: string;
  buttonText: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ProductCardComponent, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent implements AfterViewInit {
  @ViewChild('cardsContainer1') cardsContainer1!: ElementRef;
  @ViewChild('cardsWrapper1') cardsWrapper1!: ElementRef;
  @ViewChild('cardsContainer2') cardsContainer2!: ElementRef;
  @ViewChild('cardsWrapper2') cardsWrapper2!: ElementRef;
  @ViewChild('ctaSection') ctaSection!: ElementRef;
  @ViewChild('finalCTA') finalCTA!: ElementRef;

  protected readonly cards1 = signal<Card[]>([
    {
      image: '/Emi_Vestidorosa.jpeg',
      title: 'Colecciones para toda la vida',
      description: 'Descubre nuestra última colección con tonos pastel y telas fluidas.',
      buttonText: 'Ver Todo',
    },
    {
      image: '/analisis-morfologico.jpeg',
      title: 'Analisis Morfologico',
      description:
        'Descubre nuestro análisis morfológico personalizado para encontrar las prendas perfectas que resaltan tu silueta y personalidad.',
      buttonText: 'Comenzar',
    },
    {
      image: '/Emi_ModaLos80.jpeg',
      title: 'Hecho en Quevedo',
      description: 'Moda sostenible con prácticas éticas y artesanos locales.',
      buttonText: 'Conocer Más',
    },
    {
      image: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800',
      title: 'Esenciales Minimalistas',
      description: 'Piezas atemporales que forman la base de tu guardarropa.',
      buttonText: 'Explorar',
    },
  ]);

  protected readonly cards2 = signal<Card[]>([
    {
      image: '/otono.jpeg',
      title: 'Tendencias Otoño',
      description: 'Colores tierra y texturas cálidas para la nueva temporada.',
      buttonText: 'Descubrir',
    },
    {
      image: '/accesorios.jpeg',
      title: 'Accesorios Únicos',
      description: 'Complementa tu look con piezas artesanales exclusivas.',
      buttonText: 'Ver Colección',
    },
    {
      image: '/casual.jpeg',
      title: 'Estilo Casual',
      description: 'Comodidad y elegancia para tu día a día.',
      buttonText: 'Comprar',
    },
    {
      image: '/Emi_Lafuria.jpeg',
      title: 'Elegancia Nocturna',
      description: 'Prendas sofisticadas para ocasiones especiales.',
      buttonText: 'Ver Más',
    },
  ]);

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      gsap.registerPlugin(ScrollTrigger);
    }
  }

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => {
        this.initAnimations();
      }, 100);
    }
  }

  private initAnimations(): void {
    // Animación del hero
    gsap
      .timeline()
      .from('.hero-title', { y: 50, opacity: 0, duration: 1, ease: 'power3.out' })
      .from('.hero-subtitle', { y: 30, opacity: 0, duration: 0.8, ease: 'power3.out' }, '-=0.6')
      .from('.hero-button', { y: 20, opacity: 0, duration: 0.6, ease: 'power3.out' }, '-=0.4');

    // Primer scroll horizontal
    this.createHorizontalScroll(
      this.cardsContainer1.nativeElement,
      this.cardsWrapper1.nativeElement,
      false,
    );

    // Animación del CTA intermedio
    this.initCTAAnimation();

    // Segundo scroll horizontal
    this.createHorizontalScroll(
      this.cardsContainer2.nativeElement,
      this.cardsWrapper2.nativeElement,
      true,
    );

    // Animación del CTA final
    this.initFinalCTAAnimation();
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
    const badge = section.querySelector('.final-badge');
    const title = section.querySelector('.final-title');
    const subtitle = section.querySelector('.final-subtitle');
    const button = section.querySelector('#uiverse');

    const timeline = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        start: 'top 75%',
        end: 'top 25%',
        toggleActions: 'play none none reverse',
      },
    });

    timeline
      .from(badge, {
        scale: 0,
        rotation: -180,
        opacity: 0,
        duration: 0.6,
        ease: 'back.out(1.7)',
      })
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
