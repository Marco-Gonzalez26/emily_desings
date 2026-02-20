import {
  Component,
  signal,
  ViewChild,
  ElementRef,
  AfterViewInit,
  computed,
  OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { provideIcons, NgIconComponent } from '@ng-icons/core';
import {
  jamShoppingCart,
  jamUser,
  jamMenu,
  jamClose,
  jamLogOut,
  jamBox,
} from '@ng-icons/jam-icons';
import { Router, RouterLink } from '@angular/router';
import { gsap } from 'gsap';
import { AuthService } from '../../core/services/auth';
import { CartService } from '../../core/services/cart.service';

@Component({
  selector: 'app-header',
  imports: [CommonModule, NgIconComponent, RouterLink],
  providers: [provideIcons({ jamShoppingCart, jamUser, jamMenu, jamClose, jamLogOut, jamBox })],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header implements AfterViewInit, OnInit {
  @ViewChild('menuBackdrop') menuBackdrop!: ElementRef<HTMLElement>;
  @ViewChild('mobileMenu') mobileMenu!: ElementRef<HTMLElement>;
  @ViewChild('mobileOverlay') mobileOverlay!: ElementRef<HTMLElement>;

  protected readonly title = signal('EmilyDesings | Pagina Principal');
  protected readonly isMobileMenuOpen = signal(false);

  protected readonly links = signal([
    { name: 'Inicio', href: '' },
    { name: 'Catálogo', href: 'catalogo' },
    { name: 'Análisis morfológico', href: 'analisis-morfologico' },
    { name: 'Sobre Nosotros', href: 'sobre-nosotros' },
  ]);

  protected readonly isAuthenticated = computed(() => this.authService.isAuthenticated());
  protected readonly currentUser = computed(() => this.authService.currentUser());

  constructor(
    public authService: AuthService,
    public cartService: CartService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    if (this.authService.isLoggedIn()) {
      this.cartService.getCart().subscribe();
    }
  }

  ngAfterViewInit(): void {
    if (this.mobileMenu) {
      gsap.set(this.mobileMenu.nativeElement, { x: '100%' });
    }
    if (this.mobileOverlay) {
      gsap.set(this.mobileOverlay.nativeElement, { opacity: 0, display: 'none' });
    }
  }

  toggleMobileMenu(): void {
    const isOpen = !this.isMobileMenuOpen();
    this.isMobileMenuOpen.set(isOpen);

    if (isOpen) {
      this.openMobileMenu();
    } else {
      this.closeMobileMenu();
    }
  }

  logout(): void {
    this.authService.logout();
    this.closeMobileMenu();
  }

  private openMobileMenu(): void {
    document.body.style.overflow = 'hidden';

    gsap.set(this.mobileOverlay.nativeElement, { display: 'block' });
    gsap.to(this.mobileOverlay.nativeElement, {
      opacity: 1,
      duration: 0.3,
      ease: 'power2.out',
    });

    gsap.to(this.mobileMenu.nativeElement, {
      x: '0%',
      duration: 0.4,
      ease: 'power3.out',
    });

    const menuItems = this.mobileMenu.nativeElement.querySelectorAll('li');
    gsap.fromTo(
      menuItems,
      { opacity: 0, x: 20 },
      {
        opacity: 1,
        x: 0,
        duration: 0.3,
        stagger: 0.05,
        delay: 0.2,
        ease: 'power2.out',
      },
    );
  }

  private closeMobileMenu(): void {
    document.body.style.overflow = '';

    gsap.to(this.mobileOverlay.nativeElement, {
      opacity: 0,
      duration: 0.25,
      ease: 'power2.in',
      onComplete: () => {
        gsap.set(this.mobileOverlay.nativeElement, { display: 'none' });
      },
    });

    gsap.to(this.mobileMenu.nativeElement, {
      x: '100%',
      duration: 0.35,
      ease: 'power3.in',
    });
  }

  onMouseEnter(event: MouseEvent): void {
    const item = event.currentTarget as HTMLElement;
    const { left, top, width, height } = item.getBoundingClientRect();
    const backdrop = this.menuBackdrop.nativeElement;

    backdrop.style.setProperty('--left', `${left}px`);
    backdrop.style.setProperty('--top', `${top}px`);
    backdrop.style.setProperty('--width', `${width}px`);
    backdrop.style.setProperty('--height', `${height}px`);
    backdrop.style.opacity = '1';
    backdrop.style.visibility = 'visible';
  }

  onMouseLeave(): void {
    const backdrop = this.menuBackdrop.nativeElement;
    backdrop.style.opacity = '0';
    backdrop.style.visibility = 'hidden';
  }
}
