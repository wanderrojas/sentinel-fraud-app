import { Channel } from './channel.interface';
import { Country } from './country.interface';
import { Customer } from './customer.interface';
import { Merchant } from './merchant.interface';

export interface Transaction {
  transaction_id: string;
  decision: 'APPROVE' | 'REJECT' | 'REVIEW';
  confidence: number;
  risk_score: number;
  processing_time_ms: number;
  created_at: string;

  customer: Customer;
  amount: number;
  currency: string;

  country: Country;
  channel: Channel;
  merchant: Merchant;

  transaction_timestamp: string;
}
