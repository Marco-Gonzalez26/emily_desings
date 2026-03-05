import {
  Component,
  AfterViewInit,
  ElementRef,
  ViewChild,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

@Component({
  selector: 'app-about-us',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './about-us.html',
  styleUrl: './about-us.css',
})
export class AboutUsComponent implements AfterViewInit {
  @ViewChild('heroSection') heroSection?: ElementRef;
  @ViewChild('founderSection') founderSection?: ElementRef;
  @ViewChild('missionSection') missionSection?: ElementRef;
  @ViewChild('visionSection') visionSection?: ElementRef;
  @ViewChild('valuesSection') valuesSection?: ElementRef;

  values = [
    {
      title: 'Autenticidad',
      description:
        'Creemos en la moda que refleja tu verdadero yo, sin seguir tendencias pasajeras sino creando un estilo atemporal.',
      icon: '',
    },
    {
      title: 'Calidad',
      description:
        'Cada prenda es seleccionada cuidadosamente, priorizando materiales nobles y confección impecable.',
      icon: '',
    },
    {
      title: 'Sostenibilidad',
      description:
        'Nos comprometemos con prácticas éticas y sostenibles, trabajando con artesanos locales de Quevedo.',
      icon: '',
    },
    {
      title: 'Inclusividad',
      description:
        'La moda es para todos. Celebramos la diversidad de cuerpos, estilos y personalidades.',
      icon: '',
    },
  ];

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

    if (this.heroSection) {
      gsap
        .timeline()
        .from('.hero-badge', {
          scale: 0,
          opacity: 0,
          duration: 0.6,
          ease: 'back.out(1.7)',
        })
        .from(
          '.hero-title',
          {
            y: 60,
            opacity: 0,
            duration: 0.8,
            ease: 'power3.out',
          },
          '-=0.3',
        )
        .from(
          '.hero-subtitle',
          {
            y: 40,
            opacity: 0,
            duration: 0.6,
            ease: 'power3.out',
          },
          '-=0.4',
        );
    }

    // Animación de la fundadora
    if (this.founderSection) {
      gsap.from('.founder-image', {
        scrollTrigger: {
          trigger: this.founderSection.nativeElement,
          start: 'top 75%',
          toggleActions: 'play none none reverse',
        },
        x: -100,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      });

      gsap.from('.founder-content', {
        scrollTrigger: {
          trigger: this.founderSection.nativeElement,
          start: 'top 75%',
          toggleActions: 'play none none reverse',
        },
        x: 100,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      });
    }

    // Animación de Misión
    if (this.missionSection) {
      gsap.from(this.missionSection.nativeElement, {
        scrollTrigger: {
          trigger: this.missionSection.nativeElement,
          start: 'top 70%',
          toggleActions: 'play none none reverse',
        },
        y: 80,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      });
    }

    // Animación de Visión
    if (this.visionSection) {
      gsap.from(this.visionSection.nativeElement, {
        scrollTrigger: {
          trigger: this.visionSection.nativeElement,
          start: 'top 70%',
          toggleActions: 'play none none reverse',
        },
        y: 80,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      });
    }

    // Animación de Valores
    if (this.valuesSection) {
      gsap.from('.value-card', {
        scrollTrigger: {
          trigger: this.valuesSection.nativeElement,
          start: 'top 70%',
          toggleActions: 'play none none reverse',
        },
        y: 60,
        opacity: 0,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power3.out',
      });
    }
  }
}
