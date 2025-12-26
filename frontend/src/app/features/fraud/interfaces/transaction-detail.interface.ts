export interface TransactionDetail {
  transaction_id: string;
  decision: string;
  confidence: number;
  risk_score: number;
  processing_time_ms: number;
  created_at: Date;
  agent_route: string[];
  transaction: Transaction;
  customer: Customer;
  country: Country;
  channel: Channel;
  merchant: Merchant;
  signals: string[];
  citations_internal: CitationsInternal[];
  citations_external: any[];
  explanation_customer: string;
  explanation_audit: string;
  analysis_logs: AnalysisLog[];
}

export interface AnalysisLog {
  event_type: EventType;
  phase: null | string;
  agent: null;
  message: string;
  data: Data | null;
  timestamp: Date;
}

export interface Data {
  risk_level?: string;
  behavioral_score?: number;
  policies_count?: number;
  threats_count?: number;
  risk_score?: number;
  signals_count?: number;
}

export enum EventType {
  Info = 'info',
  Phase = 'phase',
  Success = 'success',
  Complete = 'complete',
}

export interface Channel {
  code: string;
  name: string;
  description: string;
}

export interface CitationsInternal {
  policy_id: string;
  version: string;
  chunk_id: string;
}

export interface Country {
  code: string;
  name: string;
  currency: string;
}

export interface Customer {
  customer_id: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
}

export interface Merchant {
  merchant_id: string;
  nombre: string;
  categoria: string;
  pais: string;
}

export interface Transaction {
  transaction_id: string;
  amount: number;
  currency: string;
  device_id: string;
  transaction_timestamp: Date;
}
