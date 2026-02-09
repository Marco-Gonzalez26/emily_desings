import {
  Component,
  AfterViewInit,
  ElementRef,
  ViewChild,
  signal,
  computed,
  PLATFORM_ID,
  Inject,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { gsap } from 'gsap';

type BodyType = 'Triángulo' | 'Triángulo Invertido' | 'Óvalo' | 'Reloj de Arena' | 'Rectángulo';

@Component({
  selector: 'app-morphology-analysis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './morphology-analysis.html',
  styleUrl: './morphology-analysis.css',
})
export class MorphologyAnalysisComponent implements AfterViewInit {
  @ViewChild('analysisSection') analysisSection?: ElementRef;
  @ViewChild('progressBar') progressBar?: ElementRef;
  @ViewChild('resultSection') resultSection?: ElementRef;

  imagePreview = signal<string | null>(null);

  form = signal({
    height: '',
    waist: '',
    shoulders: '',
    hips: '',
  });

  isAnalyzing = signal(false);
  progress = signal(0);

  result = signal<{
    bodyType: BodyType;
    probability: number;
    recommendations: { title: string; image: string }[];
    description: string;
  } | null>(null);

  canAnalyze = computed(() => {
    const f = this.form();
    return !!this.imagePreview() && f.height && f.waist && f.shoulders && f.hips;
  });

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId) && this.analysisSection) {
      setTimeout(() => {
        gsap.from(this.analysisSection!.nativeElement, {
          opacity: 0,
          y: 40,
          duration: 1,
          ease: 'power3.out',
        });
      }, 100);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    if (!file.type.startsWith('image/')) return;

    const reader = new FileReader();
    reader.onload = () => {
      if (reader.result) {
        this.imagePreview.set(reader.result as string);
        console.log('Imagen cargada correctamente');
      }
    };
    reader.readAsDataURL(file);
  }

  updateField(key: 'height' | 'waist' | 'shoulders' | 'hips') {
    return (event: Event) => {
      const value = (event.target as HTMLInputElement).value;
      this.form.update((f) => ({ ...f, [key]: value }));
      console.log('Form actualizado:', this.form());
    };
  }

  async startAnalysis(): Promise<void> {
    console.log('Iniciando análisis...');
    console.log('canAnalyze:', this.canAnalyze());
    console.log('Form:', this.form());
    console.log('Image:', this.imagePreview());

    if (!this.canAnalyze()) {
      console.log('No se puede analizar - faltan datos');
      return;
    }

    this.isAnalyzing.set(true);
    this.progress.set(0);
    this.result.set(null);

    const duration = Math.random() * 3 + 2; // 2-5 segundos
    const steps = 50;
    const increment = 100 / steps;
    const intervalTime = (duration * 1000) / steps;

    console.log('Duración del análisis:', duration);

    const progressInterval = setInterval(() => {
      const currentProgress = this.progress();
      if (currentProgress < 100) {
        this.progress.set(Math.min(100, currentProgress + increment));
      }
    }, intervalTime);

    await new Promise((resolve) => setTimeout(resolve, duration * 1000));
    clearInterval(progressInterval);
    this.progress.set(100);

    this.isAnalyzing.set(false);
    this.showResult();
  }

  private showResult(): void {
    console.log('Mostrando resultado...');
    const bodyType = this.calculateBodyType();
    const probability = Math.round(Math.random() * 24 + 72); // 72-96

    this.result.set({
      bodyType,
      probability,
      recommendations: this.getRecommendations(bodyType),
      description: this.getBodyTypeDescription(bodyType),
    });

    console.log('Resultado:', this.result());

    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => {
        if (this.resultSection) {
          // Scroll suave hacia la sección de resultados
          this.resultSection.nativeElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });

          // Animación de entrada
          gsap.from(this.resultSection.nativeElement.children, {
            opacity: 0,
            y: 30,
            stagger: 0.15,
            duration: 0.8,
            ease: 'power3.out',
          });
        }
      }, 300);
    }
  }

  private calculateBodyType(): BodyType {
    const f = this.form();
    const waist = Number(f.waist);
    const shoulders = Number(f.shoulders);
    const hips = Number(f.hips);

    console.log('Calculando tipo de cuerpo:', { waist, shoulders, hips });

    // Triángulo (pera): caderas más anchas que hombros
    if (hips > shoulders + 5) return 'Triángulo';

    // Triángulo Invertido: hombros más anchos que caderas
    if (shoulders > hips + 5) return 'Triángulo Invertido';

    // Óvalo (manzana): cintura más ancha
    if (waist > hips && waist > shoulders) return 'Óvalo';

    // Reloj de Arena: hombros y caderas similares, cintura marcada
    if (Math.abs(hips - shoulders) < 5 && waist < hips - 10) return 'Reloj de Arena';

    // Rectángulo: medidas similares
    return 'Rectángulo';
  }

  private getBodyTypeDescription(type: BodyType): string {
    const descriptions: Record<BodyType, string> = {
      Triángulo:
        'Tus caderas son más anchas que tus hombros, creando una silueta femenina y equilibrada. Las prendas que agregan volumen en la parte superior te favorecerán.',
      'Triángulo Invertido':
        'Tus hombros son más anchos que tus caderas. Te favorecen las prendas que equilibran tu figura agregando volumen en la parte inferior.',
      Óvalo:
        'Tu cintura es la parte más ancha de tu cuerpo. Las prendas fluidas y los cortes imperio te quedarán fantásticos.',
      'Reloj de Arena':
        '¡La figura más codiciada! Tus hombros y caderas están balanceados con una cintura definida. Casi todo te queda bien, especialmente las prendas entalladas.',
      Rectángulo:
        'Tus hombros, cintura y caderas tienen medidas similares. Las prendas con volumen y las capas crearán curvas hermosas en tu figura.',
    };
    return descriptions[type];
  }

  private getRecommendations(type: BodyType): { title: string; image: string }[] {
    const base = 'https://images.unsplash.com/';

    const map: Record<BodyType, { title: string; image: string }[]> = {
      Triángulo: [
        {
          title: 'Blusas Estructuradas',
          image: `${base}photo-1624206112918-f140f087f9b5?w=800&auto=format&fit=crop`,
        },
        {
          title: 'Pantalones Rectos',
          image: `${base}photo-1594633312681-425c7b97ccd1?w=800&auto=format&fit=crop`,
        },
      ],
      'Triángulo Invertido': [
        {
          title: 'Faldas A-line',
          image: `${base}photo-1583496661160-fb5886a0aaaa?w=800&auto=format&fit=crop`,
        },
        {
          title: 'Tops Fluidos',
          image: `${base}photo-1618932260643-eee4a2f652a6?w=800&auto=format&fit=crop`,
        },
      ],
      Óvalo: [
        {
          title: 'Vestidos Imperio',
          image: `${base}photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop`,
        },
        {
          title: 'Abrigos Abiertos',
          image: `${base}photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop`,
        },
      ],
      'Reloj de Arena': [
        {
          title: 'Vestidos Entallados',
          image: `${base}photo-1566174053879-31528523f8ae?w=800&auto=format&fit=crop`,
        },
        {
          title: 'Cinturones Statement',
          image: `${base}photo-1618932260643-eee4a2f652a6?w=800&auto=format&fit=crop`,
        },
      ],
      Rectángulo: [
        {
          title: 'Capas y Volumen',
          image: `${base}photo-1591369822096-ffd140ec948f?w=800&auto=format&fit=crop`,
        },
        {
          title: 'Blazers Estructurados',
          image: `/sobre-nosotros.jpg.jpeg`,
        },
      ],
    };

    return map[type];
  }
}
