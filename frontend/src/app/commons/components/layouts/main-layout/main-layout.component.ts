import { Component, EventEmitter, Output } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { MenuItem } from 'primeng/api';
import { HeaderComponent } from '../header/header.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [...SHARED_IMPORTS, RouterOutlet, HeaderComponent],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss',
})
export class MainLayoutComponent {
  sidebarVisible = true;

  constructor(private router: Router) {}

  menuItems: MenuItem[] = [
    {
      label: 'Dashboard',
      icon: 'pi pi-chart-bar',
      command: () => this.navigateTo(''),
    },
    {
      label: 'Nueva transacción(IA)',
      icon: 'pi pi-search',
      command: () => this.navigateTo('analyze'),
    },
    {
      label: 'Historial de transacciones',
      icon: 'pi pi-history',
      command: () => this.navigateTo('history'),
    },
    {
      label: 'HITL',
      icon: 'pi pi-user-edit',
      command: () => this.navigateTo('hitl'),
    },
  ];

  toggleSidebar() {
    this.sidebarVisible = !this.sidebarVisible;
  }

  navigateTo(path: string) {
    this.router.navigate([path]);
  }
}
