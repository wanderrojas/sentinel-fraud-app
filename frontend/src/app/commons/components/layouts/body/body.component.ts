import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-body',
  standalone: false,
  templateUrl: './body.component.html',
  styleUrl: './body.component.scss',
})
export class BodyComponent {
  sidebarVisible = true;

  constructor(private router: Router) {}

  menuItems: MenuItem[] = [
    {
      label: 'Dashboard',
      icon: 'pi pi-chart-bar',
      command: () => this.navigateTo(''),
    },
    {
      label: 'Nuevo análisis / IA',
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
