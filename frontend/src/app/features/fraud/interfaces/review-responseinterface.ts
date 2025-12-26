export interface ReviewResponse {
  case_id: string;
  status: string;
  reviewer_id: string;
  reviewer_decision: string;
  reviewer_notes: null;
  reviewed_at: Date;
  success: boolean;
  message: string;
}
