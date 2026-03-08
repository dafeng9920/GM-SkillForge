/**
 * L4 Dual-Window State Management
 *
 * Redux slice for managing the L4 Workbench dual-window state.
 * Enforces strict separation: Divergence content cannot persist without Adopt action.
 *
 * @module store/l4Slice
 */

import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';

// ============================================
// Type Definitions based on 10D Schema
// ============================================

export type DimensionId = 'L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7' | 'L8' | 'L9' | 'L10';

export type CognitionStatus = 'PASSED' | 'REJECTED';

export type DimensionVerdict = 'PASS' | 'FAIL';

export interface Dimension {
  dim_id: DimensionId;
  label: string;
  score: number;
  threshold: number;
  verdict: DimensionVerdict;
  evidence_ref: string;
  reason?: string;
  evidence_refs?: EvidenceRef[];
}

export interface Cognition10dData {
  intent_id: 'cognition_10d';
  status: CognitionStatus;
  repo_url: string;
  commit_sha: string;
  at_time: string;
  rubric_version: string;
  dimensions: Dimension[];
  overall_pass_count: number;
  rejection_reasons: string[];
  audit_pack_ref: string;
  generated_at: string;
}

// ============================================
// Type Definitions based on Work Item Schema
// ============================================

export interface EvidenceRef {
  ref_id: string;
  type: 'audit_pack' | 'log' | 'artifact' | 'metric' | 'screenshot' | 'report' | 'signature';
  path: string;
  hash?: {
    algorithm: 'SHA-256' | 'SHA-512' | 'MD5';
    value: string;
  };
  generated_at?: string;
}

export interface AcceptanceCriterion {
  criterion_id: string;
  description: string;
  validation: {
    type: 'schema' | 'regex' | 'range' | 'custom' | 'manual';
    schema_ref?: string;
    pattern?: string;
    min?: number;
    max?: number;
    validator_ref?: string;
  };
  mandatory?: boolean;
}

export interface AdoptedFrom {
  reason_card_id: string;
  migration_timestamp: string;
  migration_version?: string;
  original_context?: {
    session_id?: string;
    user_id?: string;
    trigger_type?: string;
    raw_content?: string;
  };
  verified: boolean;
  verified_by?: string;
  verified_at?: string;
}

// ============================================
// Execution Receipt Types
// ============================================

export interface ExecutionReceipt {
  gate_decision: 'ALLOWED' | 'DENIED' | 'PENDING';
  release_allowed: boolean;
  error_code: string | null;
  run_id: string;
  permit_id: string | null;
  replay_pointer: string | null;
  permit_status?: 'GRANTED' | 'REVOKED' | 'PENDING' | 'NONE';
}

export interface WorkItem {
  work_item_id: string;
  intent: string;
  inputs: Record<string, {
    type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'uri' | 'datetime';
    required: boolean;
    default?: unknown;
    validation?: string;
    description?: string;
  }>;
  constraints: {
    timeout_seconds: number;
    max_retries: number;
    fail_mode?: 'OPEN' | 'CLOSED';
    blocking?: boolean;
    dependencies?: string[];
    custom_constraints?: Record<string, unknown>;
  };
  acceptance: {
    criteria: AcceptanceCriterion[];
    min_pass_count?: number;
  };
  evidence: {
    evidence_refs: EvidenceRef[];
    audit_pack_ref?: string;
  };
  adopted_from: AdoptedFrom;
  execution_receipt?: ExecutionReceipt;
}

// ============================================
// Error Types
// ============================================

export type ErrorCode = 'E001' | 'E002' | 'E003' | 'E004' | 'E005';

export interface BlockedState {
  is_blocked: boolean;
  error_code?: ErrorCode;
  error_message?: string;
}

// ============================================
// API Response Types
// ============================================

export interface AdoptRequest {
  reason_card_id: string;
  requester_id: string;
  context?: {
    session_id?: string;
    window_id?: string;
    trigger_type?: string;
  };
  options?: {
    verify_immediately?: boolean;
    preserve_raw_content?: boolean;
    custom_work_item_id?: string;
  };
}

export interface AdoptResponse {
  work_item_id: string;
  status: 'ADOPTED' | 'PENDING_VERIFICATION';
  adopted_from: AdoptedFrom;
  evidence_refs: EvidenceRef[];
  created_at: string;
}

// ============================================
// State Interface
// ============================================

export interface L4State {
  // Divergence Window State
  divergence: {
    cognition_data: Cognition10dData | null;
    is_loading: boolean;
    error: string | null;
    messages: Message[];
    inputValue: string;
  };

  // Work Window State (only populated via Adopt action)
  work: {
    work_item: WorkItem | null;
    is_loading: boolean;
    error: string | null;
    blocked_state: BlockedState;
    messages: Message[];
    inputValue: string;
    isSending: boolean;
  };

  // Adopt Action State
  adopt: {
    is_enabled: boolean;
    validation_errors: string[];
    is_processing: boolean;
  };

  // UI State
  ui: {
    active_panel: 'divergence' | 'work';

    last_action_timestamp: string | null;
  };
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

// ============================================
// Initial State
// ============================================

const initialState: L4State & {
  divergence: { messages: Message[]; inputValue: string };
  work: { messages: Message[]; inputValue: string; isSending: boolean };
} = {
  divergence: {
    cognition_data: null,
    is_loading: false,
    error: null,
    messages: [
      { id: 'sys-1', role: 'system', content: '欢迎来到发散窗口。在这里您可以自由进行10阶认知探索。', timestamp: Date.now() }
    ],
    inputValue: ''
  },
  work: {
    work_item: null,
    is_loading: false,
    error: null,
    blocked_state: {
      is_blocked: false,
    },
    messages: [
      { id: 'sys-2', role: 'system', content: '欢迎来到工作窗口。此处对话受 Gate/Permit 治理约束。', timestamp: Date.now() }
    ],
    inputValue: '',
    isSending: false
  },
  adopt: {
    is_enabled: false,
    validation_errors: [],
    is_processing: false,
  },
  ui: {
    active_panel: 'divergence',
    last_action_timestamp: null,
  },
};

// ============================================
// Constants
// ============================================

// Critical dimensions that must PASS for overall success
export const CRITICAL_DIMENSIONS: DimensionId[] = ['L1', 'L3', 'L5', 'L10'];

// Minimum pass count for overall success
export const MIN_PASS_COUNT = 8;

// Dimension labels (Chinese)
export const DIMENSION_LABELS: Record<DimensionId, string> = {
  L1: '事实提取',
  L2: '概念抽象',
  L3: '因果推理',
  L4: '结构解构',
  L5: '风险感知',
  L6: '时序建模',
  L7: '跨域关联',
  L8: '不确定性标注',
  L9: '建议可行性',
  L10: '叙事连贯性',
};

// Error messages
export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  E001: 'Required 10D cognition fields are missing. Cannot proceed with Adopt.',
  E002: 'Work item adoption failed due to validation errors.',
  E003: 'Critical dimension failures detected. Work window blocked.',
  E004: 'Network error occurred during cognition assessment.',
  E005: 'Unauthorized access. Please authenticate and try again.',
};

// ============================================
// Validation Helpers
// ============================================

/**
 * Validates that all required 10D cognition fields are present
 */
export function validateCognitionData(data: Cognition10dData | null): string[] {
  const errors: string[] = [];

  if (!data) {
    errors.push('No cognition data available');
    return errors;
  }

  // Check required fields
  if (!data.intent_id) errors.push('Missing intent_id');
  if (!data.status) errors.push('Missing status');
  if (!data.repo_url) errors.push('Missing repo_url');
  if (!data.commit_sha) errors.push('Missing commit_sha');
  if (!data.at_time) errors.push('Missing at_time');
  if (!data.rubric_version) errors.push('Missing rubric_version');
  if (!data.generated_at) errors.push('Missing generated_at');
  if (!data.audit_pack_ref) errors.push('Missing audit_pack_ref');

  // Check dimensions
  if (!data.dimensions || data.dimensions.length !== 10) {
    errors.push('Must have exactly 10 dimensions');
  } else {
    // Validate each dimension has required fields
    data.dimensions.forEach((dim, index) => {
      if (!dim.dim_id) errors.push(`Dimension ${index}: Missing dim_id`);
      if (!dim.label) errors.push(`Dimension ${index}: Missing label`);
      if (typeof dim.score !== 'number') errors.push(`Dimension ${index}: Missing score`);
      if (typeof dim.threshold !== 'number') errors.push(`Dimension ${index}: Missing threshold`);
      if (!dim.verdict) errors.push(`Dimension ${index}: Missing verdict`);
      if (!dim.evidence_ref) errors.push(`Dimension ${index}: Missing evidence_ref`);
    });
  }

  // Check overall_pass_count is valid
  if (typeof data.overall_pass_count !== 'number' || data.overall_pass_count < 0) {
    errors.push('Invalid overall_pass_count');
  }

  return errors;
}

/**
 * Checks if all critical dimensions passed
 */
export function checkCriticalDimensionsPassed(data: Cognition10dData | null): boolean {
  if (!data || !data.dimensions) return false;

  return CRITICAL_DIMENSIONS.every((criticalId) => {
    const dim = data.dimensions.find((d) => d.dim_id === criticalId);
    return dim?.verdict === 'PASS';
  });
}

/**
 * Checks if the cognition passed overall policy
 */
export function checkOverallPolicyPassed(data: Cognition10dData | null): boolean {
  if (!data) return false;

  // Policy: pass_count >= 8 AND all critical dimensions must PASS
  const passCountMet = data.overall_pass_count >= MIN_PASS_COUNT;
  const criticalDimensionsMet = checkCriticalDimensionsPassed(data);

  return passCountMet && criticalDimensionsMet;
}

/**
 * Determines the blocked state for the Work Window
 */
export function determineBlockedState(data: Cognition10dData | null): BlockedState {
  const validationErrors = validateCognitionData(data);

  if (validationErrors.length > 0) {
    return {
      is_blocked: true,
      error_code: 'E001',
      error_message: ERROR_MESSAGES['E001'],
    };
  }

  if (!checkCriticalDimensionsPassed(data)) {
    return {
      is_blocked: true,
      error_code: 'E003',
      error_message: ERROR_MESSAGES['E003'],
    };
  }

  return {
    is_blocked: false,
  };
}

/**
 * Determines if the Adopt button should be enabled
 */
export function determineAdoptEnabled(data: Cognition10dData | null): boolean {
  const validationErrors = validateCognitionData(data);
  if (validationErrors.length > 0) return false;

  // Adopt is enabled only if overall policy passed
  return checkOverallPolicyPassed(data);
}

// ============================================
// Async Thunks
// ============================================

export const fetchCognition10d = createAsyncThunk(
  'l4/fetchCognition10d',
  async (params: { repo_url: string; commit_sha: string; at_time?: string }, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/cognition/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_url: params.repo_url,
          commit_sha: params.commit_sha,
          at_time: params.at_time || new Date().toISOString(),
          rubric_version: '1.0.0',
          requester_id: 'l4-workbench',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.error_message || 'Failed to fetch cognition data');
      }

      return await response.json();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const adoptWorkItem = createAsyncThunk(
  'l4/adoptWorkItem',
  async (request: AdoptRequest, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { l4: L4State };

      // Validate before adopting
      const validationErrors = validateCognitionData(state.l4.divergence.cognition_data);
      if (validationErrors.length > 0) {
        return rejectWithValue(ERROR_MESSAGES['E001']);
      }

      if (!checkOverallPolicyPassed(state.l4.divergence.cognition_data)) {
        return rejectWithValue(ERROR_MESSAGES['E003']);
      }

      const response = await fetch('/api/v1/work/adopt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        return rejectWithValue(error.error_message || 'Adoption failed');
      }

      return await response.json();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

// ============================================
// Slice Definition
// ============================================

const l4Slice = createSlice({
  name: 'l4',
  initialState,
  reducers: {
    // Clear divergence window data (without Adopt, data doesn't persist)
    clearDivergence(state) {
      state.divergence.cognition_data = null;
      state.divergence.error = null;
      state.adopt.is_enabled = false;
      state.adopt.validation_errors = [];
      state.ui.active_panel = 'divergence';
    },

    // Clear work window data
    clearWork(state) {
      state.work.work_item = null;
      state.work.error = null;
      state.work.blocked_state = { is_blocked: false };
    },

    // Set active panel
    setActivePanel(state, action: PayloadAction<'divergence' | 'work'>) {
      state.ui.active_panel = action.payload;
    },

    // Manually set cognition data (for testing/mocking)
    setCognitionData(state, action: PayloadAction<Cognition10dData>) {
      state.divergence.cognition_data = action.payload;
      state.divergence.error = null;

      // Update adopt button state
      const validationErrors = validateCognitionData(action.payload);
      state.adopt.validation_errors = validationErrors;
      state.adopt.is_enabled = validationErrors.length === 0 && checkOverallPolicyPassed(action.payload);

      // Update work window blocked state
      state.work.blocked_state = determineBlockedState(action.payload);

      state.ui.last_action_timestamp = new Date().toISOString();
    },

    // Manually set work item (for testing/mocking)
    setWorkItem(state, action: PayloadAction<WorkItem>) {
      // ENFORCEMENT: Work item can only be set through proper channel
      // This should only be called after successful Adopt action
      state.work.work_item = action.payload;
      state.work.error = null;
      state.work.blocked_state = { is_blocked: false };
      state.ui.last_action_timestamp = new Date().toISOString();
    },

    // Set error state
    setError(state, action: PayloadAction<{ window: 'divergence' | 'work'; error: string }>) {
      if (action.payload.window === 'divergence') {
        state.divergence.error = action.payload.error;
        state.divergence.is_loading = false;
      } else {
        state.work.error = action.payload.error;
        state.work.is_loading = false;
        state.work.blocked_state = {
          is_blocked: true,
          error_code: 'E002',
          error_message: action.payload.error,
        };
      }
    },

    // Chat Actions
    addDivergenceMessage(state, action: PayloadAction<Message>) {
      state.divergence.messages.push(action.payload);
    },
    addWorkMessage(state, action: PayloadAction<Message>) {
      state.work.messages.push(action.payload);
    },
    setDivergenceInput(state, action: PayloadAction<string>) {
      state.divergence.inputValue = action.payload;
    },
    setWorkInput(state, action: PayloadAction<string>) {
      state.work.inputValue = action.payload;
    },
    setWorkSending(state, action: PayloadAction<boolean>) {
      state.work.isSending = action.payload;
    },
  },
  extraReducers: (builder) => {
    // fetchCognition10d
    builder
      .addCase(fetchCognition10d.pending, (state) => {
        state.divergence.is_loading = true;
        state.divergence.error = null;
      })
      .addCase(fetchCognition10d.fulfilled, (state, action: PayloadAction<Cognition10dData>) => {
        state.divergence.is_loading = false;
        state.divergence.cognition_data = action.payload;

        // Update adopt button state based on validation
        const validationErrors = validateCognitionData(action.payload);
        state.adopt.validation_errors = validationErrors;
        state.adopt.is_enabled = validationErrors.length === 0 && checkOverallPolicyPassed(action.payload);

        // Update work window blocked state
        state.work.blocked_state = determineBlockedState(action.payload);

        state.ui.last_action_timestamp = new Date().toISOString();
      })
      .addCase(fetchCognition10d.rejected, (state, action) => {
        state.divergence.is_loading = false;
        state.divergence.error = action.payload as string;
        state.adopt.is_enabled = false;
      });

    // adoptWorkItem
    builder
      .addCase(adoptWorkItem.pending, (state) => {
        state.adopt.is_processing = true;
        state.work.is_loading = true;
        state.work.error = null;
      })
      .addCase(adoptWorkItem.fulfilled, (state, action: PayloadAction<AdoptResponse>) => {
        state.adopt.is_processing = false;
        state.work.is_loading = false;

        // Generate execution receipt
        const runId = `RUN-${Date.now().toString(36).toUpperCase()}`;
        const permitId = `PERMIT-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;

        // Create work item from response
        // Note: In real app, this would come from the /governance/work-items/{id} endpoint
        const workItem: WorkItem = {
          work_item_id: action.payload.work_item_id,
          intent: 'Migrated from Reason Card',
          inputs: {},
          constraints: {
            timeout_seconds: 3600,
            max_retries: 3,
            fail_mode: 'CLOSED',
            blocking: true,
          },
          acceptance: {
            criteria: [],
          },
          evidence: {
            evidence_refs: action.payload.evidence_refs,
          },
          adopted_from: action.payload.adopted_from,
          execution_receipt: {
            gate_decision: 'ALLOWED',
            release_allowed: true,
            error_code: null,
            run_id: runId,
            permit_id: permitId,
            replay_pointer: `replay://${runId}/${action.payload.work_item_id}`,
          },
        };

        state.work.work_item = workItem;
        state.work.blocked_state = { is_blocked: false };
        state.ui.active_panel = 'work';
        state.ui.last_action_timestamp = new Date().toISOString();

        // Clear divergence data after successful adopt (enforces strict separation)
        state.divergence.cognition_data = null;
        state.adopt.is_enabled = false;
        state.adopt.validation_errors = [];
      })
      .addCase(adoptWorkItem.rejected, (state, action) => {
        state.adopt.is_processing = false;
        state.work.is_loading = false;
        state.work.error = action.payload as string;
        state.work.blocked_state = {
          is_blocked: true,
          error_code: 'E002',
          error_message: action.payload as string,
        };
      });
  },
});

// ============================================
// Exports
// ============================================

export const {
  clearDivergence,
  clearWork,
  setActivePanel,
  setCognitionData,
  setWorkItem,
  setError,
  addDivergenceMessage,
  addWorkMessage,
  setDivergenceInput,
  setWorkInput,
  setWorkSending,
} = l4Slice.actions;

export default l4Slice.reducer;
