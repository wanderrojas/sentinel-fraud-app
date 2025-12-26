import { environment } from '../../../../environments/environment';
import { Component, inject, OnInit } from '@angular/core';
import { NavigationService } from '../../services/navigation.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-notfound',
  standalone: false,
  templateUrl: './notfound.component.html',
  styleUrl: './notfound.component.css',
})
export class NotfoundComponent implements OnInit {
  public previousUrl: string = '';
  route = inject(Router);

  ngOnInit(): void {
    this.previousUrl = sessionStorage.getItem('notFoundUrl') || '';

    console.log('La URL previa que no se encontró:', this.previousUrl);
  }
  goHome(): void {
    sessionStorage.removeItem('notFoundUrl');
    this.route.navigateByUrl('');
  }
}
