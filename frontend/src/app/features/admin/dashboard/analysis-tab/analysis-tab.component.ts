import { Component, OnInit, signal, inject, PLATFORM_ID, afterNextRender } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { DashboardService } from '../../../../core/services/dashboard.service';
import { forkJoin } from 'rxjs';

Chart.register(...registerables);

@Component({
  selector: 'app-analysis-tab',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analysis-tab.component.html',
  styleUrl: './analysis-tab.component.css',
})
export class AnalysisTabComponent implements OnInit {
  private platformId = inject(PLATFORM_ID);
  private dashboardService = inject(DashboardService);

  // Charts
  private conversionPorTipoChart?: Chart;
  private analisisPorMesChart?: Chart;

  // Data
  topProductos = signal<any[]>([]);
  distribucionTipos = signal<any>(null);
  conversionPorTipo = signal<any>(null);
  cargando = signal(true);

  constructor() {
    if (isPlatformBrowser(this.platformId)) {
      afterNextRender(() => {
        this.cargarDatos();
      });
    }
  }

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      this.cargarDatos();
    }
  }

  private cargarDatos(): void {
    this.cargando.set(true);

    forkJoin({
      distribucion: this.dashboardService.obtenerAnalisisPorTipo(),
      conversion: this.dashboardService.obtenerConversionPorTipo(),
      topProductos: this.dashboardService.obtenerProductosMasRecomendados(10),
    }).subscribe({
      next: (datos) => {
        this.distribucionTipos.set(datos.distribucion);
        this.conversionPorTipo.set(datos.conversion);
        this.topProductos.set(datos.topProductos);

        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => {
            this.crearGraficos(datos);
          }, 100);
        }

        this.cargando.set(false);
      },
      error: (error) => {
        console.error('Error cargando análisis IA:', error);
        this.cargando.set(false);
      },
    });
  }

  private crearGraficos(datos: any): void {
    this.crearConversionPorTipoChart(datos.conversion.labels, datos.conversion.valores);
    this.crearAnalisisPorMesChart(datos.distribucion.labels, datos.distribucion.valores);
  }

  private crearConversionPorTipoChart(labels: string[], valores: number[]): void {
    const ctx = document.getElementById('conversionPorTipoChart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Conversión %',
            data: valores,
            backgroundColor: '#D4A5A5',
            borderRadius: 8,
            barThickness: 40,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#3E352F',
            padding: 12,
            callbacks: {
              label: (ctx) => `${ctx.parsed.y}% conversión`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: '#F5EDE3' },
            ticks: {
              color: '#8B7F76',
              callback: (val) => `${val}%`,
            },
          },
          x: {
            grid: { display: false },
            ticks: { color: '#8B7F76' },
          },
        },
      },
    };

    this.conversionPorTipoChart = new Chart(ctx, config);
  }

  private crearAnalisisPorMesChart(labels: string[], valores: number[]): void {
    const ctx = document.getElementById('analisisPorMesChart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Análisis Realizados',
            data: valores,
            borderColor: '#D4A5A5',
            backgroundColor: 'rgba(212, 165, 165, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#3E352F',
            padding: 12,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#F5EDE3' },
            ticks: { color: '#8B7F76' },
          },
          x: {
            grid: { display: false },
            ticks: { color: '#8B7F76' },
          },
        },
      },
    };

    this.analisisPorMesChart = new Chart(ctx, config);
  }

  async exportarPDF(): Promise<void> {
    if (typeof window === 'undefined') return;

    try {
      const html2canvas = (await import('html2canvas')).default;
      const { jsPDF } = await import('jspdf');

      const element = document.getElementById('analysis-tab-content');

      if (!element) {
        console.error('Elemento no encontrado para exportar PDF');
        return;
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#FEFEFA',
        windowWidth: element.scrollWidth,
        windowHeight: element.scrollHeight,
      });

      const imgData = canvas.toDataURL('image/jpeg', 0.98);
      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4',
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth;
      const imgHeight = (canvas.height * pdfWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = 0;

      // Primera página
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      // Páginas adicionales si el contenido es muy largo
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

      // Cambiar el nombre según el tab
      pdf.save(`dashboard-analisis-ia-${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error('Error al exportar PDF:', error);
      
    }
  }
  calculateAverageConversion(): number {
    const data = this.conversionPorTipo();
    if (!data?.valores || data.valores.length === 0) {
      return 0;
    }
    const sum = data.valores.reduce((a: any, b: any) => a + b, 0);
    return parseFloat((sum / data.valores.length).toFixed(1));
  }

  getTotalAnalysis(): number {
    const data = this.distribucionTipos();
    if (!data?.valores || data.valores.length === 0) {
      return 0;
    }
    return data.valores.reduce((a: number, b: number) => a + b, 0);
  }
  ngOnDestroy(): void {
    this.conversionPorTipoChart?.destroy();
    this.analisisPorMesChart?.destroy();
  }
}
