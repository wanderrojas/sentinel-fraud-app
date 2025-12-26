import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnChanges } from '@angular/core';
import { HelperService } from '@commons/services/helper.service';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { TransactionDetail } from '@features/fraud/interfaces/transaction-detail.interface';
import { FraudService } from '@features/fraud/services/fraud.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';

@Component({
  selector: 'app-transaction-detail',
  standalone: true,
  imports: [...SHARED_IMPORTS, CommonModule],
  templateUrl: './transaction-detail.component.html',
  styleUrl: './transaction-detail.component.scss',
})
export class TransactionDetailComponent implements OnChanges {
  @Input() transactionId: string | null | undefined = null;
  @Input() activeIndex: string | null | undefined = null;

  helperService = inject(HelperService);
  fraudService = inject(FraudService);
  transaction: TransactionDetail | null = null;

  ngOnChanges(): void {
    if (this.transactionId) {
      this.loadTransaction();
    }
  }

  loadTransaction() {
    if (!this.transactionId) return;

    this.fraudService.getTransactionDetail(this.transactionId).subscribe({
      next: (resp) => {
        this.transaction = resp;
      },
    });
  }

  getDecisionSeverity(decision: string) {
    return FraudHelpers.getDecisionSeverity(decision);
  }

  getResultClass(decision: string) {
    return FraudHelpers.getResultClass(decision);
  }

  getLogColor(eventType: string): string {
    switch (eventType) {
      case 'phase':
        return '#3b82f6'; // azul fuerte
      case 'success':
        return '#10b981'; // verde
      case 'info':
        return '#6b7280'; // gris
      default:
        return '#d1d5db';
    }
  }

  getLogIcon(eventType: string): string {
    switch (eventType) {
      case 'phase':
        return 'pi pi-arrow-right';
      case 'success':
        return 'pi pi-check-circle';
      case 'info':
        return 'pi pi-info-circle';
      default:
        return 'pi pi-info';
    }
  }
}
