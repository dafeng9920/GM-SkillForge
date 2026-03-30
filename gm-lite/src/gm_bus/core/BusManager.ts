/**
 * GM Shared Task Bus - BusManager Core (Seed Implementation)
 *
 * Minimal core class for GM Bus operations.
 * Scope: Seed only - no watcher, no runtime, no auto-send.
 *
 * Version: 1.0.0-seed
 * Task: BM1 - Antigravity-1
 */

import * as fs from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';

// ============================================================================
// Type Imports
// ============================================================================

import type {
  TaskEnvelope,
  DispatchPacket,
  Receipt,
  Writeback,
  EscalationPack,
  StateLog,
  UUID,
  TaskStatus,
  ISO8601
} from '../types';

// ============================================================================
// Core Exceptions
// ============================================================================

export class BusError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly context?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'BusError';
  }
}

export class ValidationError extends BusError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', context);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends BusError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, 'NOT_FOUND', context);
    this.name = 'NotFoundError';
  }
}

// ============================================================================
// Directory Structure Definition
// ============================================================================

export interface BusPaths {
  root: string;
  manifest: string;
  outbox: string;
  inbox: string;
  writeback: string;
  escalation: string;
  archive: string;
  schemas: string;
  validators: string;
  projectors: string;
}

export class BusPathsBuilder {
  static build(rootPath: string): BusPaths {
    const root = path.resolve(rootPath);
    return {
      root,
      manifest: path.join(root, 'manifest'),
      outbox: path.join(root, 'outbox'),
      inbox: path.join(root, 'inbox'),
      writeback: path.join(root, 'writeback'),
      escalation: path.join(root, 'escalation'),
      archive: path.join(root, 'archive'),
      schemas: path.join(root, 'schemas'),
      validators: path.join(root, 'validators'),
      projectors: path.join(root, 'projectors')
    };
  }
}

// ============================================================================
// Minimal Read/Write Operations (Seed Level)
// ============================================================================

export interface ReadResult<T> {
  data: T;
  path: string;
  exists: boolean;
}

export interface WriteResult {
  path: string;
  written: boolean;
  timestamp: ISO8601;
}

export class BusFileSystem {
  private paths: BusPaths;

  constructor(paths: BusPaths) {
    this.paths = paths;
  }

  /**
   * Read JSON file from bus directory
   */
  async read<T>(dir: keyof BusPaths, filename: string): Promise<ReadResult<T>> {
    const targetDir = this.paths[dir];
    const filePath = path.join(targetDir, filename);

    if (!fs.existsSync(filePath)) {
      return { data: null as T, path: filePath, exists: false };
    }

    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content) as T;
      return { data, path: filePath, exists: true };
    } catch (err) {
      throw new BusError(
        `Failed to read file: ${filePath}`,
        'READ_ERROR',
        { originalError: err }
      );
    }
  }

  /**
   * Write JSON file to bus directory
   */
  async write<T>(dir: keyof BusPaths, filename: string, data: T): Promise<WriteResult> {
    const targetDir = this.paths[dir];
    const filePath = path.join(targetDir, filename);

    // Ensure directory exists
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    try {
      const content = JSON.stringify(data, null, 2);
      fs.writeFileSync(filePath, content, 'utf-8');
      return {
        path: filePath,
        written: true,
        timestamp: new Date().toISOString() as ISO8601
      };
    } catch (err) {
      throw new BusError(
        `Failed to write file: ${filePath}`,
        'WRITE_ERROR',
        { originalError: err }
      );
    }
  }

  /**
   * Delete file from bus directory
   */
  async delete(dir: keyof BusPaths, filename: string): Promise<boolean> {
    const targetDir = this.paths[dir];
    const filePath = path.join(targetDir, filename);

    if (!fs.existsSync(filePath)) {
      return false;
    }

    try {
      fs.unlinkSync(filePath);
      return true;
    } catch (err) {
      throw new BusError(
        `Failed to delete file: ${filePath}`,
        'DELETE_ERROR',
        { originalError: err }
      );
    }
  }

  /**
   * List files in a bus directory
   */
  async list(dir: keyof BusPaths, pattern?: string): Promise<string[]> {
    const targetDir = this.paths[dir];

    if (!fs.existsSync(targetDir)) {
      return [];
    }

    try {
      const files = fs.readdirSync(targetDir);
      if (pattern) {
        const regex = new RegExp(pattern);
        return files.filter(f => regex.test(f));
      }
      return files;
    } catch (err) {
      throw new BusError(
        `Failed to list directory: ${targetDir}`,
        'LIST_ERROR',
        { originalError: err }
      );
    }
  }
}

// ============================================================================
// BusManager - Core Class (Seed Implementation)
// ============================================================================

export interface BusManagerConfig {
  /** Root directory for .gm_bus */
  rootDir: string;
  /** Participant identifier for this instance */
  participantId: string;
  /** Enable debug logging */
  debug?: boolean;
}

export class BusManager {
  private readonly paths: BusPaths;
  private readonly fs: BusFileSystem;
  private readonly config: BusManagerConfig;
  private initialized: boolean = false;

  constructor(config: BusManagerConfig) {
    this.config = config;
    this.paths = BusPathsBuilder.build(config.rootDir);
    this.fs = new BusFileSystem(this.paths);
  }

  /**
   * Initialize the bus directory structure
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    // Create all required directories
    const dirs: (keyof BusPaths)[] = [
      'manifest', 'outbox', 'inbox', 'writeback',
      'escalation', 'archive', 'schemas', 'validators', 'projectors'
    ];

    for (const dir of dirs) {
      const dirPath = this.paths[dir];
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
        this.debug(`Created directory: ${dirPath}`);
      }
    }

    this.initialized = true;
    this.debug('BusManager initialized');
  }

  /**
   * Create a new task envelope
   */
  async createTask(input: {
    type: string;
    initiator: string;
    priority?: 'low' | 'normal' | 'high' | 'critical';
    payload: unknown;
    metadata?: Record<string, unknown>;
  }): Promise<TaskEnvelope> {
    this.ensureInitialized();

    const taskId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const envelope: TaskEnvelope = {
      id: taskId,
      type: input.type,
      version: '1.0.0',
      created_at: now,
      updated_at: now,
      status: 'pending',
      initiator: input.initiator,
      assignee: null,
      priority: input.priority ?? 'normal',
      payload_sha256: this.computeHash(input.payload),
      metadata: input.metadata ?? {}
    };

    // Write to manifest
    await this.fs.write('manifest', `${taskId}.json`, envelope);
    this.debug(`Task created: ${taskId}`);

    return envelope;
  }

  /**
   * Read task envelope by ID
   */
  async getTask(taskId: UUID): Promise<TaskEnvelope> {
    this.ensureInitialized();

    const result = await this.fs.read<TaskEnvelope>('manifest', `${taskId}.json`);

    if (!result.exists) {
      throw new NotFoundError(
        `Task not found: ${taskId}`,
        { taskId }
      );
    }

    return result.data;
  }

  /**
   * Create dispatch packet for task delivery
   */
  async createDispatch(input: {
    taskId: UUID;
    toParticipant: string;
    fromParticipant?: string;
    dispatchType?: 'direct' | 'broadcast' | 'delegated';
    payload: unknown;
    expiresAt?: ISO8601;
  }): Promise<DispatchPacket> {
    this.ensureInitialized();

    // Verify task exists
    await this.getTask(input.taskId);

    const packetId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const packet: DispatchPacket = {
      packet_id: packetId,
      task_id: input.taskId,
      dispatch_type: input.dispatchType ?? 'direct',
      from_participant: input.fromParticipant ?? this.config.participantId,
      to_participant: input.toParticipant,
      created_at: now,
      expires_at: input.expiresAt ?? null,
      payload: {
        type: {},
        data: input.payload
      },
      dispatch_metadata: {},
      signature: null
    };

    // Write to outbox
    await this.fs.write('outbox', `${packetId}.json`, packet);
    this.debug(`Dispatch created: ${packetId} -> ${input.toParticipant}`);

    return packet;
  }

  /**
   * Accept a dispatched task (create receipt)
   */
  async acceptTask(packetId: UUID, acceptedBy: string): Promise<Receipt> {
    this.ensureInitialized();

    // Read from inbox
    const result = await this.fs.read<DispatchPacket>('inbox', `${packetId}.json`);

    if (!result.exists) {
      throw new NotFoundError(
        `Dispatch packet not found: ${packetId}`,
        { packetId }
      );
    }

    const packet = result.data;
    const receiptId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const receipt: Receipt = {
      receipt_id: receiptId,
      packet_id: packetId,
      task_id: packet.task_id,
      accepted_by: acceptedBy,
      accepted_at: now,
      response_type: 'accept',
      response_reason: null,
      estimated_completion: null,
      conditions: [],
      signature: null
    };

    // Write to writeback
    await this.fs.write('writeback', `${receiptId}.json`, receipt);
    this.debug(`Receipt created: ${receiptId}`);

    return receipt;
  }

  /**
   * Submit task result (create writeback)
   */
  async submitResult(input: {
    taskId: UUID;
    executedBy: string;
    resultType: 'success' | 'failure' | 'partial' | 'timeout';
    message: string;
    output?: unknown;
    error?: unknown;
    artifacts?: string[];
  }): Promise<Writeback> {
    this.ensureInitialized();

    const writebackId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const writeback: Writeback = {
      writeback_id: writebackId,
      task_id: input.taskId,
      receipt_id: null,
      executed_by: input.executedBy,
      completed_at: now,
      result_type: input.resultType,
      result_data: {
        status_code: null,
        message: input.message,
        output: input.output ?? null,
        error: input.error ?? null
      },
      artifacts: input.artifacts ?? [],
      metrics: {
        duration_ms: null,
        memory_used_mb: null,
        cpu_usage_percent: null
      }
    };

    // Write to writeback
    await this.fs.write('writeback', `${writebackId}.json`, writeback);
    this.debug(`Writeback created: ${writebackId}`);

    return writeback;
  }

  /**
   * Create escalation pack
   */
  async escalate(input: {
    taskId: UUID;
    originalPacketId: UUID;
    escalatedBy: string;
    escalationType: 'timeout' | 'failure' | 'conflict' | 'manual' | 'resource';
    severity: 'low' | 'medium' | 'high' | 'critical';
    reason: string;
    requiredAction: 'retry' | 'reassign' | 'abort' | 'manual_review' | 'notify';
  }): Promise<EscalationPack> {
    this.ensureInitialized();

    const escalationId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const escalation: EscalationPack = {
      escalation_id: escalationId,
      task_id: input.taskId,
      original_packet_id: input.originalPacketId,
      escalated_by: input.escalatedBy,
      escalated_at: now,
      escalation_type: input.escalationType,
      severity: input.severity,
      reason: input.reason,
      context: {
        error_trace: null,
        retry_count: 0,
        last_state: '',
        involved_participants: [input.escalatedBy]
      },
      required_action: input.requiredAction,
      target_participant: null,
      deadline: null
    };

    // Write to escalation
    await this.fs.write('escalation', `${escalationId}.json`, escalation);
    this.debug(`Escalation created: ${escalationId}`);

    return escalation;
  }

  /**
   * Append state log entry
   */
  async logState(input: {
    taskId: UUID;
    eventType: 'created' | 'dispatched' | 'accepted' | 'started' | 'progressed' | 'completed' | 'failed' | 'escalated' | 'archived';
    actor: string;
    previousState: string | null;
    currentState: string;
    changes: Record<string, unknown>;
    references?: string[];
  }): Promise<StateLog> {
    this.ensureInitialized();

    // Get next sequence number
    const existingLogs = await this.fs.list('archive', `${input.taskId}-*.json`);
    const sequenceNumber = existingLogs.length + 1;

    const logId = randomUUID() as UUID;
    const now = new Date().toISOString() as ISO8601;

    const log: StateLog = {
      log_id: logId,
      task_id: input.taskId,
      sequence_number: sequenceNumber,
      occurred_at: now,
      event_type: input.eventType,
      actor: input.actor,
      event_data: {
        previous_state: input.previousState,
        current_state: input.currentState,
        changes: input.changes,
        references: input.references ?? []
      },
      append_only: true
    };

    // Write to archive
    await this.fs.write('archive', `${input.taskId}-${sequenceNumber.toString().padStart(6, '0')}-${logId}.json`, log);
    this.debug(`State log: ${input.taskId} - ${input.eventType}`);

    return log;
  }

  /**
   * Get current paths
   */
  getPaths(): BusPaths {
    return { ...this.paths };
  }

  /**
   * Check if initialized
   */
  isInitialized(): boolean {
    return this.initialized;
  }

  // ==========================================================================
  // Private Helpers
  // ==========================================================================

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new BusError(
        'BusManager not initialized. Call initialize() first.',
        'NOT_INITIALIZED'
      );
    }
  }

  private debug(message: string): void {
    if (this.config.debug) {
      console.log(`[BusManager] ${message}`);
    }
  }

  private computeHash(data: unknown): string {
    // Seed implementation: simple hash placeholder
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
}

// ============================================================================
// Factory Function
// ============================================================================

export function createBusManager(config: BusManagerConfig): BusManager {
  return new BusManager(config);
}

// ============================================================================
// Export
// ============================================================================

export default BusManager;
