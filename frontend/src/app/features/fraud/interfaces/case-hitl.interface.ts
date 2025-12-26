import { Transaction } from './transaction.interface';

export interface CaseHitl {
  case_id: string;
  decision_recommendation: string;
  confidence: number;
  status: string;
  created_at: Date;
  created_by: string;
  reviewer_id: null;
  reviewer_decision: null;
  reviewer_notes: null;
  reviewed_at: null;
  transaction: Transaction;
}
