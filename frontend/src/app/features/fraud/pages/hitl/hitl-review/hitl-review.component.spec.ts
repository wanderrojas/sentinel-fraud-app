import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HitlReviewComponent } from './hitl-review.component';

describe('HitlReviewComponent', () => {
  let component: HitlReviewComponent;
  let fixture: ComponentFixture<HitlReviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [HitlReviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HitlReviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
