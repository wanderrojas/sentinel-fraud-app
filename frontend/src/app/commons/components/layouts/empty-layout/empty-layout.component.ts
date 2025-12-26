import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderTopComponent } from '../header-top/header-top.component';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';

@Component({
  selector: 'app-empty-layout',
  standalone: true,
  imports: [RouterOutlet, ...SHARED_IMPORTS],
  templateUrl: './empty-layout.component.html',
  styleUrl: './empty-layout.component.css',
})
export class EmptyLayoutComponent {}
