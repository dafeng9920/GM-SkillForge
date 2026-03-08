/**
 * Frontend component contracts for the NEW-GM intent migration.
 *
 * Goal:
 * - Keep frontend unblocked with a projection model based on current SkillForge APIs.
 * - Allow future switch to backend-native `five_stage_plan` / `three_cards` fields.
 */

export type GateDecision = 'ALLOW' | 'BLOCK' | 'DENY' | 'REQUIRES_CHANGES';

export interface N8nErrorEnvelope {
  ok: false;
  error_code: string;
  blocked_by: string;
  message: string;
  evidence_ref?: string;
  run_id: string;
  forbidden_field_evidence?: Record<string, unknown> | null;
  required_changes?: string[];
}

export interface N8nSuccessEnvelope<TData = Record<string, unknown>> {
  ok: true;
  data: TData;
  gate_decision: GateDecision;
  release_allowed: boolean;
  evidence_ref: string;
  run_id: string;
}

// ---------------------------------------------------------------------------
// Current API payload contracts (subset used by frontend)
// ---------------------------------------------------------------------------

export interface RunIntentData {
  intent_id: string;
  repo_url: string;
  commit_sha: string;
  at_time?: string;
  execution_status?: string;
  permit_id?: string | null;
  validation_timestamp?: string | null;
  context?: Record<string, unknown> | null;
}

export type RunIntentResponse = N8nSuccessEnvelope<RunIntentData> | N8nErrorEnvelope;

export interface FetchPackData {
  run_id: string;
  evidence_ref: string;
  replay_pointer?: {
    snapshot_ref?: string | null;
    at_time?: string | null;
    revision?: string | null;
    evidence_bundle_ref?: string | null;
  } | null;
  query_at_time?: string;
  fetched_at?: string;
  [key: string]: unknown;
}

export type FetchPackResponse = N8nSuccessEnvelope<FetchPackData> | N8nErrorEnvelope;

export interface RagResultItem {
  id?: string;
  score?: number;
  text?: string;
  source?: string;
  [key: string]: unknown;
}

export interface QueryRagData {
  query?: string;
  results?: RagResultItem[];
  replay_pointer?: {
    at_time?: string;
    [key: string]: unknown;
  } | null;
  [key: string]: unknown;
}

export type QueryRagResponse = N8nSuccessEnvelope<QueryRagData> | N8nErrorEnvelope;

// ---------------------------------------------------------------------------
// Five-stage projection model (UI-only, NEW-GM intent)
// ---------------------------------------------------------------------------

export type FiveStageId = 'trigger' | 'collect' | 'process' | 'deliver' | 'report';
export type FiveStageStatus = 'idle' | 'running' | 'success' | 'failed' | 'blocked';

export interface FiveStageItem {
  id: FiveStageId;
  title: string;
  status: FiveStageStatus;
  summary: string;
  // Key evidence refs or IDs shown in stage cards.
  refs?: string[];
  // Raw payload snapshot for drawer/details panel.
  payload?: Record<string, unknown>;
}

export interface FiveStageViewModel {
  run_id: string;
  evidence_ref?: string;
  stages: FiveStageItem[];
}

// ---------------------------------------------------------------------------
// Three-cards projection model (UI-only, NEW-GM intent)
// ---------------------------------------------------------------------------

export type ThreeCardKind = 'understanding' | 'plan' | 'execution_contract';

export interface ThreeCard {
  kind: ThreeCardKind;
  title: string;
  bullets: string[];
  confidence?: number;
  refs?: string[];
  payload?: Record<string, unknown>;
}

export interface ThreeCardsViewModel {
  run_id: string;
  evidence_ref?: string;
  cards: ThreeCard[];
}

// ---------------------------------------------------------------------------
// Combined orchestration projection
// ---------------------------------------------------------------------------

export interface OrchestrationProjection {
  run_id: string;
  evidence_ref?: string;
  gate_decision?: GateDecision;
  release_allowed?: boolean;
  five_stage: FiveStageViewModel;
  three_cards: ThreeCardsViewModel;
}

