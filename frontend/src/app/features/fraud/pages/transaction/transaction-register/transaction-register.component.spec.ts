import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransactionRegisterComponent } from './transaction-register.component';

describe('AnalyzeComponent', () => {
  let component: TransactionRegisterComponent;
  let fixture: ComponentFixture<TransactionRegisterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TransactionRegisterComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TransactionRegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
