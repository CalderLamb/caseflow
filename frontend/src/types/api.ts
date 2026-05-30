// Core API types — mirrors the backend Pydantic schemas exactly.
// Generated from OpenAPI schema in CI; do not hand-edit.

export type Confidence = "high" | "medium" | "low";

export type WeaknessCategory =
  | "law"
  | "facts"
  | "data"
  | "contradiction"
  | "procedure";

export type ItemState =
  | "detected"
  | "evaluated"
  | "draft_requested"
  | "drafted"
  | "scheduled"
  | "reviewed"
  | "done"
  | "dismissed"
  | "snoozed";

export type DraftStatus =
  | "pending_review"
  | "edited"
  | "approved"
  | "rejected"
  | "superseded";

export interface Citation {
  kind: "document" | "email" | "event";
  ref: string;
  page?: number;
  label: string;
}

export interface ScoreFactor {
  label: string;
  weight: number;
}

export interface PredictedWeakness {
  category: WeaknessCategory;
  note: string;
}

export interface AssembledFact {
  text: string;
  citation: Citation;
}

export interface ReviewSlot {
  start: string;
  end: string;
}

export interface CaseItem {
  id: string;
  matter_id: string;
  matter_name: string;
  kind: string;
  state: ItemState;
  trigger_text: string;
  trigger_citations: Citation[];
  proposed_action: string | null;
  consequence_score: number | null;
  score_factors: ScoreFactor[];
  predicted_confidence: Confidence | null;
  predicted_weaknesses: PredictedWeakness[];
  draft_id: string | null;
  review_slot: ReviewSlot | null;
  created_at: string;
  updated_at: string;
}

export interface CaseItemDetail extends CaseItem {
  assembled_facts: AssembledFact[];
}

export interface Annotation {
  span_start: number;
  span_end: number;
  category: WeaknessCategory;
  note: string;
}

export interface Draft {
  id: string;
  case_item_id: string;
  body: string;
  confidence: Confidence;
  annotations: Annotation[];
  token_cost: number;
  status: DraftStatus;
  created_at: string;
  updated_at: string;
}

export interface DraftEstimate {
  predicted_confidence: Confidence | null;
  estimated_tokens: number;
  estimated_length: string;
  predicted_weaknesses: { category: WeaknessCategory; note: string }[];
}

export interface Matter {
  id: string;
  name: string;
  type: string;
  status: string;
  court: string | null;
  case_number: string | null;
  opened_date: string | null;
  sol_date: string | null;
  drive_folder_id: string | null;
  client_name: string;
  open_item_count: number;
  total_token_cost: number;
}

export interface MatterDetail extends Matter {
  items: CaseItem[];
  deadlines: {
    id: string;
    description: string;
    due_date: string;
    is_malpractice_class: boolean;
  }[];
  documents: {
    id: string;
    title: string;
    doc_type: string | null;
    source: string;
    processed: boolean;
  }[];
  chronology: {
    id: string;
    date_of_entry: string | null;
    provider: string | null;
    findings: string | null;
    flagged: boolean;
  }[];
  facts: {
    id: string;
    text: string;
    issue_tags: string[];
    confidence: Confidence | null;
  }[];
  cost_by_month: { month: string; tokens: number }[];
}

export interface QueueResponse {
  items: CaseItem[];
  total: number;
  page: number;
  page_size: number;
}
