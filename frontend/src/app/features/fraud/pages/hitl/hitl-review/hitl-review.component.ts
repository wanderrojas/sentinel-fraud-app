import {
  Component,
  EventEmitter,
  inject,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MessageType } from '@commons/constants/MessageType';
import { HelperService } from '@commons/services/helper.service';
import { SpinnerService } from '@commons/services/spinner.service';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { AuthService } from '@features/auth/services/auth.service';
import { DecisionType } from '@features/fraud/enums/decision.enum';
import { CaseHitl } from '@features/fraud/interfaces/case-hitl.interface';
import { FraudService } from '@features/fraud/services/fraud.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
import { ConfirmationService } from 'primeng/api';
import { TransactionDetailComponent } from '../../history/transaction-detail/transaction-detail.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-hitl-review',
  standalone: true,
  imports: [...SHARED_IMPORTS, TransactionDetailComponent, CommonModule],
  templateUrl: './hitl-review.component.html',
  styleUrl: './hitl-review.component.scss',
})
export class HitlReviewComponent implements OnInit, OnChanges {
  @Input() selectedCase: CaseHitl | null = null;
  @Input() reviewDecision: any = null;
  @Output() responseReview: EventEmitter<any> = new EventEmitter<any>();

  fb = inject(FormBuilder);
  helperService = inject(HelperService);
  fraudService = inject(FraudService);
  confirmationService = inject(ConfirmationService);
  authService = inject(AuthService);
  spinnerService = inject(SpinnerService);

  reviewForm!: FormGroup;
  formSubmitted = false;
  submitReview = false;
  currentUser: any;
  reviewOptions = [
    { label: 'Aprobar', value: DecisionType.APPROVE },
    { label: 'Challenge', value: DecisionType.CHALLENGE },
    { label: 'Bloquear', value: DecisionType.BLOCK },
  ];

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.initForm();

    this.applyDefaults();
  }

  applyDefaults() {
    if (!this.reviewForm) return;

    if (this.currentUser) {
      this.reviewForm.patchValue({
        reviewer_id: this.currentUser.usuario,
        decision: this.reviewDecision,
      });
    }
  }

  initForm() {
    this.reviewForm = this.fb.group({
      reviewer_id: ['', Validators.required],
      decision: ['', Validators.required],
      notes: [''],
    });
  }

  getStatusSeverity(
    status: string | undefined
  ): 'success' | 'warn' | 'danger' | 'info' | null {
    switch (status) {
      case 'APPROVED':
        return 'success';
      case 'BLOCK':
      case 'REJECTED':
        return 'danger';
      case 'PENDING':
        return 'warn';
      default:
        return 'info';
    }
  }

  getDecisionSeverity(decision: string) {
    return FraudHelpers.getDecisionSeverity(decision);
  }
  ngOnChanges(changes: SimpleChanges) {
    if (changes['reviewDecision'] && this.reviewForm) {
      this.reviewForm.patchValue({
        decision: this.reviewDecision,
      });
    }
    if (
      changes['selectedCase'] &&
      !changes['selectedCase'].currentValue &&
      this.reviewForm
    ) {
      this.resetForm();
    }
  }

  isInvalid(controlName: string) {
    const control = this.reviewForm.get(controlName);
    return control?.invalid && (control.touched || this.formSubmitted);
  }

  confirmReview() {
    if (!this.helperService.validateForm(this.reviewForm)) return;

    this.confirmationService.confirm({
      message: `¿Confirmar revisión del caso ${this.selectedCase?.case_id}?`,
      header: 'Confirmar Revisión',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Sí',
      rejectLabel: 'No',
      acceptIcon: 'pi pi-check',
      rejectIcon: 'pi pi-times',
      acceptButtonStyleClass: 'p-button-success',
      rejectButtonStyleClass: 'p-button-secondary',

      accept: () => {
        this.submitReview = true;
        this.onSubmitReview();
      },
    });
  }

  resetForm() {
    if (!this.reviewForm) return;

    this.reviewForm.reset();
    this.formSubmitted = false;
    this.submitReview = false;

    this.applyDefaults();
  }

  onSubmitReview() {
    if (!this.selectedCase) return;

    this.fraudService
      .reviewCase(this.reviewForm.value, this.selectedCase.case_id)
      .subscribe({
        next: (resp) => {
          this.helperService.showMessage(MessageType.SUCCESS, resp.message);
          this.responseReview.emit(resp);
          this.resetForm();
        },
        error: (error) => this.spinnerService.hideFullScreen(),
      });
  }
}
