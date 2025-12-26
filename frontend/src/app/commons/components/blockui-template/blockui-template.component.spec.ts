import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BlockuiTemplateComponent } from './blockui-template.component';

describe('BlockuiTemplateComponent', () => {
  let component: BlockuiTemplateComponent;
  let fixture: ComponentFixture<BlockuiTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [BlockuiTemplateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BlockuiTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
