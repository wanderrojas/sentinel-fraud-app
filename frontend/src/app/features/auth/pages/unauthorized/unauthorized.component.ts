import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';

@Component({
  selector: 'app-unauthorized',
  standalone: true,
  imports: [...SHARED_IMPORTS],
  templateUrl: './unauthorized.component.html',
  styleUrl: './unauthorized.component.css',
})
export class UnauthorizedComponent {
  route = inject(Router);

  gotToHome(): void {
    this.route.navigateByUrl('');
  }
}
