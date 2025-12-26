import { Component, inject } from '@angular/core';
import { ExcelService } from '@commons/services/excel.service';
import { HelperService } from '@commons/services/helper.service';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { DecisionType } from '@features/fraud/enums/decision.enum';
import { TransactionHistory } from '@features/fraud/interfaces/fraud.models';
import { FraudService } from '@features/fraud/services/fraud.service';
import { MasterService } from '@features/fraud/services/master.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
import { TagModule } from 'primeng/tag';
import { TransactionDetailComponent } from '../transaction-detail/transaction-detail.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [...SHARED_IMPORTS, TransactionDetailComponent, CommonModule],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css',
})
export class HistoryComponent {
  masterService = inject(MasterService);
  helperService = inject(HelperService);
  excelService = inject(ExcelService);

  transactions: TransactionHistory[] = [];
  loading = false;
  showReviewDialog = false;
  transactionId: string | null = null;
  customers: any[] = [];

  searchTerm = '';
  decisionFilter: DecisionType | null = null;

  filterOptions = {
    customer_id: null,
    decision: null,
    limit: 1000,
  };

  decisionOptions = [
    { label: 'Aprobadas', value: DecisionType.APPROVE },
    { label: 'Challenge', value: DecisionType.CHALLENGE },
    { label: 'Bloqueadas', value: DecisionType.BLOCK },
    { label: 'Escaladas', value: DecisionType.ESCALATE_TO_HUMAN },
  ];

  constructor(private fraudApi: FraudService) {}

  ngOnInit() {
    this.loadTransactions();
    this.loadCustomers();
  }

  /**
   * Carga el historial de transacciones
   * - Usa los filtros definidos en `filterOptions`.
   * - Actualiza `transactions` y controla el indicador de carga.
   */
  loadTransactions() {
    this.loading = true;
    const params = this.helperService.toQueryParams(this.filterOptions);
    this.fraudApi.getTransactionHistory(params).subscribe({
      next: (response) => {
        this.transactions = response.transactions;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading history:', error);
        this.loading = false;
      },
    });
  }

  /**
   * Muestra los detalles de una transacción.
   * - Guarda el ID de la transacción seleccionada.
   * - Abre el diálogo de revisión.
   */
  viewDetails(transaction: TransactionHistory) {
    this.transactionId = transaction.transaction_id;
    this.showReviewDialog = true;
  }

  /**
   * Prepara las transacciones en formato legible y exporta a Excel.
   * - Descarga automáticamente el archivo Excel.
   */
  exportData() {
    const exportData = this.transactions.map((r) => ({
      'ID TRANSACCIÓN': r.transaction_id,
      DECISIÓN: r.decision,
      'CONFIANZA (%)': Math.round(r.confidence * 100),
      'PUNTAJE DE RIESGO': Number(r.risk_score.toFixed(2)),
      'TIEMPO DE PROCESAMIENTO (MS)': Math.round(r.processing_time_ms),
      'FECHA DE CREACIÓN': new Date(r.created_at).toLocaleString(),

      MONTO: r.amount,
      MONEDA: r.currency,

      'ID CLIENTE': r.customer.customer_id,
      'NOMBRE DEL CLIENTE': `${r.customer.nombre} ${r.customer.apellido}`,

      PAÍS: r.country.name,
      CANAL: r.channel.name,

      'ID COMERCIO': r.merchant.merchant_id,
      'NOMBRE DEL COMERCIO': r.merchant.nombre,
      'CATEGORÍA DEL NEGOCIO': r.merchant.categoria,

      'FECHA DE TRANSACCIÓN': new Date(
        r.transaction_timestamp
      ).toLocaleString(),
    }));

    this.excelService.exportJsonToExcel(exportData);
  }

  /**
   * Obtiene la severidad de una decisión para usar en etiquetas o estilos.
   * @param decision Decisión del caso (BLOCK, APPROVED, PENDING, etc.)
   * @returns Severidad correspondiente (success, warn, danger, etc.)
   */
  getDecisionSeverity(decision: string) {
    return FraudHelpers.getDecisionSeverity(decision);
  }

  /**
   * Carga la lista de clientes desde el servicio maestro.
   * - Asigna la respuesta a la variable `customers`.
   */
  loadCustomers() {
    this.masterService.getCustomers().subscribe({
      next: (resp) => {
        this.customers = resp;
      },
      error: () => {},
    });
  }
}
