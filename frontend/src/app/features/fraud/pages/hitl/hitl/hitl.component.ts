import { Component, ViewChild } from '@angular/core';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { DecisionType } from '@features/fraud/enums/decision.enum';
import { CaseHitl } from '@features/fraud/interfaces/case-hitl.interface';
import { FraudService } from '@features/fraud/services/fraud.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
import { HitlReviewComponent } from '../hitl-review/hitl-review.component';
import { CommonModule } from '@angular/common';
@Component({
  selector: 'app-hitl',
  standalone: true,
  imports: [...SHARED_IMPORTS, HitlReviewComponent, CommonModule],
  templateUrl: './hitl.component.html',
  styleUrl: './hitl.component.css',
})
export class HitlComponent {
  cases: CaseHitl[] = [];
  loading = false;
  statusFilter: string | null = 'PENDING';

  showReviewDialog = false;
  selectedCase: CaseHitl | null = null;
  reviewDecision: DecisionType | null = DecisionType.APPROVE;

  detailVisible: boolean = false;

  constructor(private fraudApi: FraudService) {}

  ngOnInit() {
    this.loadCases();
  }

  loadCases() {
    this.loading = true;

    const request = this.statusFilter
      ? this.fraudApi.getAllCases(this.statusFilter)
      : this.fraudApi.getAllCases();

    request.subscribe({
      next: (cases) => {
        this.cases = cases;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  filterByStatus(status: string | null) {
    this.statusFilter = status;
    this.loadCases();
  }

  viewCase(caseItem: CaseHitl) {
    this.selectedCase = caseItem;
    this.reviewDecision = DecisionType.APPROVE;
    this.showReviewDialog = true;
  }

  reviewCase(caseItem: CaseHitl, decision: string) {
    this.selectedCase = caseItem;
    this.reviewDecision = decision as DecisionType;
    this.showReviewDialog = true;
  }

  getDecisionSeverity(decision: string) {
    return FraudHelpers.getDecisionSeverity(decision);
  }

  getStatusSeverity(status: string) {
    return FraudHelpers.getStatusSeverity(status);
  }

  handleResponseHitlReview(event: any) {
    this.showReviewDialog = false;
    this.loadCases();
  }

  onCloseReviewDialog() {
    this.showReviewDialog = false;
    this.selectedCase = null;
    this.reviewDecision = null;
  }
}
