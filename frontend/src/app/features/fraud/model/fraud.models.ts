import { DecisionType } from '../enums/decision.enum';
import { HITLStatus } from '../enums/hitl-status.enum';

export interface Transaction {
  transaction_id: string;
  customer_id: string;
  amount: number;
  currency: string;
  country: string;
  channel: string;
  device_id: string;
  timestamp: string;
  merchant_id: string;
}

export interface TransactionAnalysisRequest {
  transaction: Transaction;
  customer_behavior?: CustomerBehavior;
}

export interface CustomerBehavior {
  customer_id: string;
  usual_amount_avg: number;
  usual_hours: string;
  usual_countries: string;
  usual_devices: string;
}

export interface DecisionResponse {
  transaction_id: string;
  decision: DecisionType;
  confidence: number;
  signals: string[];
  citations_internal: InternalCitation[];
  citations_external: ExternalCitation[];
  explanation_customer: string;
  explanation_audit: string;
  agent_route: string;
  processing_time_ms: number;
}

export interface InternalCitation {
  policy_id: string;
  chunk_id: string;
  version: string;
}

export interface ExternalCitation {
  url: string;
  summary: string;
}

export interface HITLCase {
  case_id: string;
  transaction: Transaction;
  decision_recommendation: DecisionType;
  confidence: number;
  signals: string[];
  citations_internal: InternalCitation[];
  citations_external: ExternalCitation[];
  agent_route: string;
  created_at: string;
  status: HITLStatus;
  reviewer_id?: string;
  reviewer_decision?: DecisionType;
  reviewer_notes?: string;
  reviewed_at?: string;
}

export interface TransactionHistoryNOVALE {
  transaction_id: string;
  decision: DecisionType;
  confidence: number;
  risk_score: number;
  processing_time_ms: number;
  created_at: string;
}

export interface Statistics {
  total_transactions: number;
  total_decisions: number;
  decisions_by_type: {
    APPROVE: number;
    CHALLENGE: number;
    BLOCK: number;
    ESCALATE_TO_HUMAN: number;
  };
  hitl_cases: {
    pending: number;
    approved: number;
    rejected: number;
    total: number;
  };
}
