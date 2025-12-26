import { HttpClient } from '@angular/common/http';
import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { filter, Subscription } from 'rxjs';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { SpinnerService } from '@commons/services/spinner.service';
import { SESSION_STORAGE_CLEANUP } from '@commons/constants/SessionStorageConfig';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { CommonModule } from '@angular/common';

interface WeatherForecast {
  date: string;
  temperatureC: number;
  temperatureF: number;
  summary: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: true,
  imports: [...SHARED_IMPORTS, RouterOutlet, CommonModule],
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit, OnDestroy {
  spinnerMessage: string = 'Cargando...';
  private messageSubscription?: Subscription;

  constructor(private spinnerService: SpinnerService, private router: Router) {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.cleanupSessionStorage(event.url);
      });
  }

  ngOnInit(): void {
    this.messageSubscription = this.spinnerService.message$.subscribe(
      (message) => (this.spinnerMessage = message)
    );
  }

  private cleanupSessionStorage(currentUrl: string): void {
    SESSION_STORAGE_CLEANUP.forEach(({ key, excludeRoutes }) => {
      // Solo limpia si la URL actual NO está en las rutas excluidas
      const shouldClean = !excludeRoutes.some((route) =>
        currentUrl.includes(route)
      );

      if (shouldClean) {
        sessionStorage.removeItem(key);
      }
    });
  }

  ngOnDestroy(): void {
    this.messageSubscription?.unsubscribe();
  }
}
