import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-blockui-template',
  standalone: false,
  templateUrl: './blockui-template.component.html',
  styleUrl: './blockui-template.component.css',
})
export class BlockuiTemplateComponent implements OnInit {
  message!: string;
  constructor() {}

  ngOnInit(): void {}
}
