import {
  Component,
  ElementRef,
  EventEmitter,
  inject,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { CommonModule } from '@angular/common';
import { HelperService } from '@commons/services/helper.service';
import { DecisionResponse } from '@features/fraud/interfaces/fraud.models';
import { FraudService } from '@features/fraud/services/fraud.service';
import { MasterService } from '@features/fraud/services/master.service';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
import { MessageService } from 'primeng/api';
import { TransactionDetailComponent } from '../../history/transaction-detail/transaction-detail.component';

@Component({
  selector: 'app-transaction-result',
  standalone: true,
  imports: [...SHARED_IMPORTS, CommonModule, TransactionDetailComponent],
  templateUrl: './transaction-result.component.html',
  styleUrl: './transaction-result.component.scss',
})
export class TransactionResultComponent implements OnChanges {
  @ViewChild('generateAnalyze') generateAnalyze?: TransactionResultComponent;
  @ViewChild('logsContainer') private logsContainer!: ElementRef;

  @Input() analyzing: boolean = false;
  @Input() formValue: any = null;
  @Output() responseAnalyze: EventEmitter<any> = new EventEmitter<any>();

  activeIndex: string = '0';

  masterService = inject(MasterService);
  helperService = inject(HelperService);
  messageService = inject(MessageService);
  fraudService = inject(FraudService);

  logs: any[] = [];
  logsLoading: boolean = true;
  result: DecisionResponse | null = null;
  currentStreamingMessage = '';
  private shouldScroll = false;

  newTransaction = false;

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      if (this.logsContainer) {
        const el = this.logsContainer.nativeElement;
        el.scrollTop = el.scrollHeight;
      }
    } catch (err) {}
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (
      changes['analyzing'] &&
      changes['analyzing'].currentValue === true &&
      this.formValue
    ) {
      this.resetState();
      this.analyzeTransaction();
    }
  }

  private resetState(): void {
    this.logs = [];
    this.result = null;
    this.currentStreamingMessage = 'Iniciando análisis...';
    this.logsLoading = true;
  }

  analyzeTransaction() {
    this.analyzing = true;
    this.logsLoading = true; // mostrar loader al iniciar
    this.result = null;

    console.log('data', this.formValue);

    // Suscribirse al servicio
    this.fraudService.analyzeWithStreaming(this.formValue).subscribe({
      next: (event) => {
        this.handleStreamEvent(event);
      },
      error: (error) => this.handleStreamError(error),
      complete: () => (this.analyzing = false),
    });
  }

  handleStreamEvent(event: any) {
    // Desmarcar el anterior
    if (this.logs.length > 0) {
      this.logs[this.logs.length - 1].active = false;
    }

    const logEvent = {
      ...event,
      active: true,
    };

    this.shouldScroll = true;
    if (event.message) {
      this.currentStreamingMessage = event.message;
    }

    this.logs = [...this.logs, logEvent];

    console.log('EVENT', event);

    if (event.event === 'complete') {
      this.result = event.data;
      logEvent.active = false;
      this.analyzing = false;
      this.responseAnalyze.emit('success');
    }
  }

  private handleStreamError(error: any) {
    console.error('Error en streaming:', error);
    this.analyzing = false;

    this.messageService.add({
      severity: 'error',
      summary: 'Error',
      detail: error.message || 'Error al analizar la transacción',
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

  resetForm() {
    //const response = { success: true, message: 'Formulario reseteado' };

    // Emitir al componente padre
    this.responseAnalyze.emit('reset');
  }
}
