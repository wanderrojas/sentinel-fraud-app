import {
  Component,
  EventEmitter,
  inject,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Router } from '@angular/router';
import { SpinnerService } from '../../../services/spinner.service';
import { Menu } from 'primeng/menu';
import { AuthService } from '@features/auth/services/auth.service';
import { UserData } from '@features/auth/interfaces/auth-login-response.interface';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [...SHARED_IMPORTS],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent implements OnInit {
  @Output() toggleSidebar = new EventEmitter<void>();

  @ViewChild('userMenu') userMenu!: Menu;

  authService = inject(AuthService);
  router = inject(Router);
  spinnerService = inject(SpinnerService);
  usuario: UserData = {} as UserData;

  ngOnInit(): void {
    this.authService.currentUser$.subscribe((user) => {
      this.usuario = user || ({} as UserData);
    });
  }

  async handleLogout() {
    this.spinnerService.showFullScreen('Cerrando sesión...');

    try {
      await this.authService.logout();
      this.router.navigate(['/']);
    } catch (error) {
    } finally {
      this.spinnerService.hideFullScreen();
    }
  }

  userMenuItems: MenuItem[] = [
    {
      label: 'Perfil',
      icon: 'pi pi-user',
      command: () => this.goToProfile(),
    },
    {
      label: 'Configuración',
      icon: 'pi pi-cog',
      command: () => this.goToSettings(),
    },
    { separator: true },
    {
      label: 'Cerrar sesión',
      icon: 'pi pi-sign-out',
      command: () => this.handleLogout(),
    },
  ];

  goToProfile() {
    console.log('Ir a perfil');
  }

  goToSettings() {
    console.log('Ir a configuración');
  }

  logout() {
    console.log('Logout');
  }

  openUserMenu(event: Event) {
    event.stopPropagation();
    this.userMenu.toggle(event);
  }

  onToggleSidebar(event: Event) {
    event.stopPropagation();
    this.toggleSidebar.emit();
  }

  onAvatarClick(event: Event, menu: Menu) {
    event.stopPropagation();
    menu.toggle(event);
  }
}
