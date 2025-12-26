import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HitlComponent } from './hitl.component';

describe('HitlComponent', () => {
  let component: HitlComponent;
  let fixture: ComponentFixture<HitlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [HitlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HitlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
