import { Component, ElementRef, inject, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MessageService } from 'primeng/api';

import { SHARED_IMPORTS } from '@commons/utils/shared-modules';
import { TransactionResultComponent } from '../transaction-result/transaction-result.component';
import { CommonModule } from '@angular/common';
import { MasterService } from '@features/fraud/services/master.service';
import { HelperService } from '@commons/services/helper.service';
import { FraudService } from '@features/fraud/services/fraud.service';
import { TransactionAnalysisRequest } from '@features/fraud/interfaces/fraud.models';
import { MessageType } from '@commons/constants/MessageType';
import { Channel } from '@features/fraud/interfaces/channel.interface';
import { Country } from '@features/fraud/interfaces/country.interface';
import { Customer } from '@features/fraud/interfaces/customer.interface';
import { Merchant } from '@features/fraud/interfaces/merchant.interface';
import { TransactionRandom } from '@features/fraud/interfaces/transaction-random.interface';
import { FraudHelpers } from '@features/fraud/utils/fraud-helpers';
import { forkJoin } from 'rxjs';

export interface TransactionStreamEvent {
  event: string;
  data: any;
}

@Component({
  selector: 'app-transaction-register',
  standalone: true,
  imports: [...SHARED_IMPORTS, TransactionResultComponent],
  templateUrl: './transaction-register.component.html',
  styleUrl: './transaction-register.component.scss',
})
export class TransactionRegisterComponent {
  @ViewChild('logsContainer') logsContainer?: ElementRef;

  masterService = inject(MasterService);
  fb = inject(FormBuilder);
  helperService = inject(HelperService);
  messageService = inject(MessageService);
  fraudService = inject(FraudService);

  transactionForm!: FormGroup;
  formSubmitted = false;
  showButtonNewTransaction = false;
  titleTransaction = 'Nueva Transacción';

  startAnalyze = false;
  requestDataAnalyze: TransactionAnalysisRequest =
    {} as TransactionAnalysisRequest;

  customers: Customer[] = [];
  countries: Country[] = [];
  channels: Channel[] = [];
  merchants: Merchant[] = [];

  private shouldScroll = false;

  ngOnInit() {
    this.initForm();
    this.loadInitialData();
  }

  initForm() {
    this.transactionForm = this.fb.group({
      transaction_id: [
        FraudHelpers.generateTransactionId(),
        Validators.required,
      ],
      customer_id: ['', Validators.required],
      amount: ['', [Validators.required, Validators.min(0)]],
      currency: ['PEN', Validators.required],
      country: ['', Validators.required],
      channel: ['', Validators.required],
      device_id: [FraudHelpers.generateDeviceId(), Validators.required],
      merchant_id: ['', Validators.required],
      timestamp: [, Validators.required],
    });

    this.titleTransaction = 'Nueva Transacción';
  }

  generateRandomData() {
    const data: TransactionRandom = FraudHelpers.generateRandomData();
    this.transactionForm.patchValue(data);
    this.helperService.showMessage(
      MessageType.INFO,
      `Transacción de ${data.amount} PEN generada`,
      'Datos randoms Generados'
    );
  }

  isInvalid(controlName: string) {
    const control = this.transactionForm.get(controlName);
    return control?.invalid && (control.touched || this.formSubmitted);
  }

  scrollToBottom(): void {
    try {
      if (this.logsContainer) {
        this.logsContainer.nativeElement.scrollTop =
          this.logsContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Error al hacer scroll:', err);
    }
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  resetForm() {
    this.transactionForm.reset();
    this.initForm();
    this.formSubmitted = false;
    this.startAnalyze = false;
  }

  loadInitialData() {
    forkJoin({
      customers: this.masterService.getCustomers(),
      countries: this.masterService.getCountries(),
      channels: this.masterService.getChannels(),
      merchants: this.masterService.getMerchants(),
    }).subscribe({
      next: (resp) => {
        this.customers = resp.customers;
        this.countries = resp.countries;
        this.channels = resp.channels;
        this.merchants = resp.merchants;
      },
      error: (err) => {
        console.error('Error cargando datos iniciales', err);
      },
    });
  }

  onSubmitted() {
    this.formSubmitted = true;
    if (!this.transactionForm.valid) {
      this.helperService.showMessage(
        MessageType.ERROR,
        'Error de validación de campos',
        'Por favor complete todos los campos'
      );
      return;
    }

    const formValue = this.transactionForm.value;
    this.requestDataAnalyze = {
      transaction: {
        transaction_id: formValue.transaction_id,
        customer_id: formValue.customer_id,
        amount: formValue.amount,
        currency: formValue.currency,
        country: formValue.country,
        channel: formValue.channel,
        device_id: formValue.device_id,
        merchant_id: formValue.merchant_id,
        timestamp: FraudHelpers.formatTimestamp(formValue.timestamp),
      },
    };

    this.startAnalyze = false;
    setTimeout(() => {
      this.startAnalyze = true;
      this.titleTransaction = 'Procesando transación';
    });
  }

  onResponseAnalyze(event: any) {
    console.log('event', event);
    if (event === 'success') {
      this.titleTransaction = 'Transacción culminada';
    }

    if (event === 'reset') {
      this.resetForm();
    }
  }
}
