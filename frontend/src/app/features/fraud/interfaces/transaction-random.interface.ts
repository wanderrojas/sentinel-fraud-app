export interface TransactionRandom {
  transaction_id: string;
  customer_id: string;
  amount: number;
  currency: string;
  country: string;
  channel: string;
  device_id: string;
  merchant_id: string;
  timestamp: Date;
}
