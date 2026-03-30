/**
 * GM Shared Task Bus - Protocol Object Type Definitions
 *
 * This file contains TypeScript type stubs for the 6 core protocol objects.
 * These are minimal type definitions for Light version - no implementation logic.
 *
 * Version: 1.0.0
 * Scope: Definition Only (Light)
 * Source: Copied from .gm_bus/schemas/types.ts for src/ module accessibility
 */

// ============================================================================
// Common Types
// ============================================================================

export type UUID = string;
export type ISO8601 = string;

/**
 * Task status enum
 */
export type TaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'failed' | 'escalated';

/**
 * Priority enum
 */
export type Priority = 'low' | 'normal' | 'high' | 'critical';

/**
 * Dispatch type enum
 */
export type DispatchType = 'direct' | 'broadcast' | 'delegated';

/**
 * Response type enum
 */
export type ResponseType = 'accept' | 'decline' | 'defer';

/**
 * Result type enum
 */
export type ResultType = 'success' | 'failure' | 'partial' | 'timeout';

/**
 * Escalation type enum
 */
export type EscalationType = 'timeout' | 'failure' | 'conflict' | 'manual' | 'resource';

/**
 * Severity enum
 */
export type Severity = 'low' | 'medium' | 'high' | 'critical';

/**
 * Required action enum
 */
export type RequiredAction = 'retry' | 'reassign' | 'abort' | 'manual_review' | 'notify';

/**
 * Event type enum
 */
export type EventType = 'created' | 'dispatched' | 'accepted' | 'started' | 'progressed' | 'completed' | 'failed' | 'escalated' | 'archived';

// ============================================================================
// BM2: Gate Level Definitions (Fire Control Metdata)
// ============================================================================

/**
 * Gate checkpoint states
 */
export type GateCheckpoint =
  | 'created' | 'validated' | 'rejected'     // L0 checkpoints
  | 'ready' | 'blocked' | 'released'        // L1 checkpoints
  | 'granted' | 'denied' | 'revoked'        // L2 checkpoints
  | 'verified' | 'rejected' | 'pending';    // L3 checkpoints

/**
 * Individual gate level state
 */
export interface GateLevelState {
  /** Gate enabled flag */
  enabled: boolean;
  /** Last checkpoint timestamp */
  timestamp: ISO8601 | null;
  /** Current checkpoint */
  checkpoint: GateCheckpoint;
}

/**
 * Gate levels container (Layer 2 state model)
 * Stored in: TaskEnvelope.metadata._gate_levels
 */
export interface GateLevels {
  /** L0: Initial gate - task validity check */
  L0_VALIDATION: GateLevelState;
  /** L1: Dispatch gate - target reachability check */
  L1_DISPATCH: GateLevelState;
  /** L2: Execution gate - resource readiness check */
  L2_EXECUTION: GateLevelState;
  /** L3: Writeback gate - result validity check */
  L3_WRITEBACK: GateLevelState;
}

/**
 * Fire control flags for L1 (Dispatch)
 */
export interface L1FireControlFlags {
  /** bit 0: Allow broadcast dispatch */
  BROADCAST_ALLOWED: boolean;
  /** bit 1: Allow delegation dispatch */
  DELEGATION_ALLOWED: boolean;
  /** bit 2: Require signature verification */
  SIGNATURE_REQUIRED: boolean;
  /** bit 3: Enable expiry check */
  EXPIRY_CHECK_ENABLED: boolean;
  /** bit 4-7: Reserved for future expansion */
  RESERVED: [boolean, boolean, boolean, boolean];
}

/**
 * Fire control flags for L2 (Execution)
 */
export interface L2FireControlFlags {
  /** bit 0: Allow concurrent execution */
  CONCURRENT_ALLOWED: boolean;
  /** bit 1: Allow retry on failure */
  RETRY_ALLOWED: boolean;
  /** bit 2: Require resource quota */
  QUOTA_REQUIRED: boolean;
  /** bit 3: Enable timeout check */
  TIMEOUT_CHECK_ENABLED: boolean;
  /** bit 4-7: Reserved for future expansion */
  RESERVED: [boolean, boolean, boolean, boolean];
}

/**
 * Fire control flags for L3 (Writeback)
 */
export interface L3FireControlFlags {
  /** bit 0: Require integrity verification */
  INTEGRITY_CHECK_REQUIRED: boolean;
  /** bit 1: Allow partial writeback */
  PARTIAL_ALLOWED: boolean;
  /** bit 2: Require audit signature */
  AUDIT_SIGNATURE_REQUIRED: boolean;
  /** bit 3: Enable auto archive */
  AUTO_ARCHIVE_ENABLED: boolean;
  /** bit 4-7: Reserved for future expansion */
  RESERVED: [boolean, boolean, boolean, boolean];
}

/**
 * Individual fire control level
 */
export interface FireControlLevel<T> {
  /** Bit mask (8-bit for future expansion) */
  mask: number;
  /** Decoded flags */
  flags: T;
}

/**
 * Fire control bits container (BM2 reserved structure)
 * Stored in: TaskEnvelope.metadata._fire_control
 */
export interface FireControlBits {
  /** Version identifier */
  _version: '1.0.0';
  /** L1: Dispatch fire control bits */
  L1: FireControlLevel<L1FireControlFlags>;
  /** L2: Execution fire control bits */
  L2: FireControlLevel<L2FireControlFlags>;
  /** L3: Writeback fire control bits */
  L3: FireControlLevel<L3FireControlFlags>;
}

/**
 * Extended metadata with BM2 guard fields
 * This extends the base Record<string, unknown> with typed guard fields
 */
export interface TaskEnvelopeMetadata extends Record<string, unknown> {
  /** BM2: Gate levels state (Layer 2) */
  _gate_levels?: GateLevels;
  /** BM2: Fire control bits (L1/L2/L3) */
  _fire_control?: FireControlBits;
  /** Additional user-defined metadata */
  [key: string]: unknown;
}

// ============================================================================
// Protocol Object 1: TaskEnvelope
// ============================================================================

/**
 * TaskEnvelope - Task projection view in manifest/
 *
 * Represents the authoritative projection of a task's state.
 * Stored in: .gm_bus/manifest/
 */
export interface TaskEnvelope {
  /** Task unique identifier (UUID v4) */
  id: UUID;

  /** Task type identifier */
  type: string;

  /** Protocol version (semver) */
  version: string;

  /** Creation timestamp (ISO 8601) */
  created_at: ISO8601;

  /** Last update timestamp (ISO 8601) */
  updated_at: ISO8601;

  /** Task status (Layer 1: lifecycle_status) */
  status: TaskStatus;

  /** Initiator participant identifier */
  initiator: string;

  /** Assignee participant identifier (nullable) */
  assignee: string | null;

  /** Task priority */
  priority: Priority;

  /** Payload digest for integrity verification */
  payload_sha256: string;

  /**
   * Metadata container with BM2 guard fields
   * Supports _gate_levels (Layer 2 state) and _fire_control (L1/L2/L3 bits)
   */
  metadata: TaskEnvelopeMetadata;
}

// ============================================================================
// Protocol Object 2: DispatchPacket
// ============================================================================

/**
 * Payload structure
 */
export interface Payload {
  /** Payload type definition */
  type: Record<string, unknown>;

  /** Payload actual data */
  data: unknown;
}

/**
 * DispatchPacket - Task delivery container for outbox/ → inbox/
 *
 * Encapsulates all context needed for task distribution.
 * Stored in: .gm_bus/outbox/ → .gm_bus/inbox/
 */
export interface DispatchPacket {
  /** Packet unique identifier (UUID v4) */
  packet_id: UUID;

  /** Reference to TaskEnvelope.id */
  task_id: UUID;

  /** Dispatch type */
  dispatch_type: DispatchType;

  /** Sender participant identifier */
  from_participant: string;

  /** Receiver participant identifier */
  to_participant: string;

  /** Dispatch creation time (ISO 8601) */
  created_at: ISO8601;

  /** Expiration time (ISO 8601, nullable) */
  expires_at: ISO8601 | null;

  /** Task payload data */
  payload: Payload;

  /** Dispatch metadata */
  dispatch_metadata: Record<string, unknown>;

  /** Signature (optional, for verification) */
  signature: string | null;
}

// ============================================================================
// Protocol Object 3: Receipt
// ============================================================================

/**
 * Acceptance condition
 */
export interface Condition {
  condition: string;
  value: unknown;
}

/**
 * Receipt - Acceptance confirmation writeback in writeback/
 *
 * Confirms that a receiver has accepted the task assignment.
 * Stored in: .gm_bus/writeback/
 */
export interface Receipt {
  /** Receipt unique identifier (UUID v4) */
  receipt_id: UUID;

  /** Reference to DispatchPacket.packet_id */
  packet_id: UUID;

  /** Reference to TaskEnvelope.id */
  task_id: UUID;

  /** Receiver participant identifier */
  accepted_by: string;

  /** Acceptance time (ISO 8601) */
  accepted_at: ISO8601;

  /** Response type */
  response_type: ResponseType;

  /** Response reason (optional) */
  response_reason: string | null;

  /** Estimated completion time (optional) */
  estimated_completion: ISO8601 | null;

  /** Acceptance conditions list */
  conditions: Condition[];

  /** Signature (optional) */
  signature: string | null;
}

// ============================================================================
// Protocol Object 4: Writeback
// ============================================================================

/**
 * Result data structure
 */
export interface ResultData {
  /** Status code (optional) */
  status_code: number | null;

  /** Result message */
  message: string;

  /** Output data */
  output: unknown;

  /** Error details (on failure) */
  error: unknown | null;
}

/**
 * Performance metrics
 */
export interface Metrics {
  /** Execution duration in milliseconds */
  duration_ms: number | null;

  /** Memory used in MB */
  memory_used_mb: number | null;

  /** CPU usage percentage */
  cpu_usage_percent: number | null;

  [key: string]: number | null | undefined;
}

/**
 * Writeback - Execution result writeback in writeback/
 *
 * Encapsulates the result data after task execution completion.
 * Stored in: .gm_bus/writeback/
 */
export interface Writeback {
  /** Writeback unique identifier (UUID v4) */
  writeback_id: UUID;

  /** Reference to TaskEnvelope.id */
  task_id: UUID;

  /** Reference to Receipt.receipt_id (optional) */
  receipt_id: UUID | null;

  /** Executor participant identifier */
  executed_by: string;

  /** Completion time (ISO 8601) */
  completed_at: ISO8601;

  /** Result type */
  result_type: ResultType;

  /** Result data */
  result_data: ResultData;

  /** Artifact reference path list */
  artifacts: string[];

  /** Performance metrics */
  metrics: Metrics;
}

// ============================================================================
// Protocol Object 5: EscalationPack
// ============================================================================

/**
 * Escalation context information
 */
export interface EscalationContext {
  /** Error stack trace */
  error_trace: string | null;

  /** Retry count */
  retry_count: number;

  /** Last known state */
  last_state: string;

  /** Involved participants */
  involved_participants: string[];
}

/**
 * EscalationPack - Escalation request for escalation/
 *
 * Encapsulates task exception conditions requiring escalation.
 * Stored in: .gm_bus/escalation/
 */
export interface EscalationPack {
  /** Escalation pack unique identifier (UUID v4) */
  escalation_id: UUID;

  /** Reference to TaskEnvelope.id */
  task_id: UUID;

  /** Reference to original DispatchPacket */
  original_packet_id: UUID;

  /** Escalation initiator identifier */
  escalated_by: string;

  /** Escalation initiation time (ISO 8601) */
  escalated_at: ISO8601;

  /** Escalation type */
  escalation_type: EscalationType;

  /** Severity level */
  severity: Severity;

  /** Escalation reason description */
  reason: string;

  /** Context information */
  context: EscalationContext;

  /** Required action */
  required_action: RequiredAction;

  /** Target handler (nullable) */
  target_participant: string | null;

  /** Handling deadline (optional) */
  deadline: ISO8601 | null;
}

// ============================================================================
// Protocol Object 6: StateLog
// ============================================================================

/**
 * Event data structure
 */
export interface EventData {
  /** Previous state */
  previous_state: string | null;

  /** Current state */
  current_state: string;

  /** Changed fields and values */
  changes: Record<string, unknown>;

  /** References to other object IDs */
  references: string[];
}

/**
 * StateLog - Event append-only log for archive/
 *
 * Records all state change events in a task's lifecycle.
 * Stored in: .gm_bus/archive/
 */
export interface StateLog {
  /** Log entry unique identifier (UUID v4) */
  log_id: UUID;

  /** Reference to TaskEnvelope.id */
  task_id: UUID;

  /** Event sequence number (monotonically increasing) */
  sequence_number: number;

  /** Event occurrence time (ISO 8601) */
  occurred_at: ISO8601;

  /** Event type */
  event_type: EventType;

  /** Participant performing the operation */
  actor: string;

  /** Event data */
  event_data: EventData;

  /** Append-only mode flag (always true) */
  append_only: true;
}
