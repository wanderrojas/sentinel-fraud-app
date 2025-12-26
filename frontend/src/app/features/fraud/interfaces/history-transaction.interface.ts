import { Transaction } from './transaction.interface';

export interface TransactionHistoryResponse {
  total: number;
  filters: TransactionFilters;
  transactions: Transaction[];
}

export interface TransactionFilters {
  customer_id: string | null;
  decision: string | null;
  limit: number;
}
