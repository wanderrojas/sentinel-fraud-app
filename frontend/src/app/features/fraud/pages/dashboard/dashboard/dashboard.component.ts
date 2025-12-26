import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { HelperService } from '@commons/services/helper.service';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { TransactionHistory } from '@features/fraud/interfaces/fraud.models';
import { Statistics } from '@features/fraud/model/fraud.models';
import { FraudService } from '@features/fraud/services/fraud.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [...SHARED_IMPORTS, CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent {
  helperService = inject(HelperService);

  stats: Statistics | null = null;
  recentTransactions: TransactionHistory[] = [];
  loading = false;

  filterOptionsList = {
    customer_id: null,
    decision: null,
    limit: 1000,
  };

  // Chart data
  chartData: any;
  chartOptions: any;

  constructor(private fraudApi: FraudService) {}

  ngOnInit() {
    this.loadStatistics();
    this.loadRecentTransactions();
  }

  loadStatistics() {
    this.loading = true;
    this.fraudApi.getStatistics().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.prepareChartData();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading statistics:', error);
        this.loading = false;
      },
    });
  }

  loadRecentTransactions() {
    const params = this.helperService.toQueryParams(this.filterOptionsList);
    this.fraudApi.getTransactionHistory(params).subscribe({
      next: (response) => {
        this.recentTransactions = response.transactions;
      },
      error: (error) => {
        console.error('Error loading recent transactions:', error);
      },
    });
  }

  prepareChartData() {
    if (!this.stats) return;

    const decisions = this.stats.decisions_by_type;

    this.chartData = {
      labels: ['Aprobadas', 'Challenge', 'Bloqueadas', 'Escaladas'],
      datasets: [
        {
          data: [
            decisions.APPROVE,
            decisions.CHALLENGE,
            decisions.BLOCK,
            decisions.ESCALATE_TO_HUMAN,
          ],
          backgroundColor: [
            '#10b981', // green
            '#f59e0b', // yellow
            '#ef4444', // red
            '#3b82f6', // blue
          ],
          hoverBackgroundColor: ['#059669', '#d97706', '#dc2626', '#2563eb'],
        },
      ],
    };

    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
      },
    };
  }

  getDecisionSeverity(decision: string) {
    return FraudHelpers.getDecisionSeverity(decision);
  }
}
