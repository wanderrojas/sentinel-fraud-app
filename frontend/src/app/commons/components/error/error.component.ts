import { Component, OnDestroy, OnInit } from '@angular/core';
import { filter, Subscription } from 'rxjs';
import { Router, NavigationStart, Event as RouterEvent } from '@angular/router';

@Component({
  selector: 'app-error',
  standalone: false,
  templateUrl: './error.component.html',
  styleUrl: './error.component.css',
})
export class ErrorComponent implements OnInit, OnDestroy {
  message = 'Ha ocurrido un error inesperado.';
  private routerSub?: Subscription;

  constructor(private router: Router) {}

  ngOnInit(): void {
    const storedMessage = sessionStorage.getItem('app_error_message');
    if (storedMessage) {
      this.message = storedMessage;
    }

    this.routerSub = this.router.events
      .pipe(
        filter(
          (event: RouterEvent): event is NavigationStart =>
            event instanceof NavigationStart
        )
      )
      .subscribe((event: NavigationStart) => {
        if (!event.url.startsWith('/error')) {
          sessionStorage.removeItem('app_error_message');
        }
      });
  }

  goHome(): void {
    this.router.navigateByUrl('');
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
    sessionStorage.removeItem('app_error_message');
  }
}
