/**
 * Runtime Interface Mapper
 *
 * 映射器：将真实 JSON 数据转换为前端类型
 *
 * 来源: core/runtime_interface.py v0.1
 * 用途: TASK-MAIN-04B - 前端承接主链状态、证据入口和运行结果
 */

import type {
  ArtifactKind,
  ArtifactRef,
  ArtifactManifest,
  EvidenceRef,
  GateDecision,
  MainChainStep,
  MainChainStepResult,
  MainChainStatus,
  RunResult,
  RunStatus,
} from '../types/runtimeInterface';

// =============================================================================
// 类型常量
// =============================================================================

const RUN_STATUS_MAP: Record<string, RunStatus> = {
  'pending': 'pending',
  'running': 'running',
  'success': 'success',
  'failure': 'failure',
  'blocked': 'blocked',
  'cancelled': 'cancelled',
};

const ARTIFACT_KIND_MAP: Record<string, ArtifactKind> = {
  'blueprint': 'blueprint',
  'contract': 'contract',
  'code': 'code',
  'test': 'test',
  'evidence': 'evidence',
  'config': 'config',
  'documentation': 'documentation',
  'other': 'other',
};

// =============================================================================
// 映射函数: ArtifactRef
// =============================================================================

/**
 * 将 JSON 映射为 ArtifactRef
 */
export function mapToArtifactRef(data: unknown): ArtifactRef {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid ArtifactRef data');
  }

  const obj = data as Record<string, unknown>;

  return {
    path: String(obj.path ?? ''),
    kind: ARTIFACT_KIND_MAP[String(obj.kind ?? 'other')] || 'other',
    content_hash: obj.content_hash ? String(obj.content_hash) : undefined,
    size_bytes: obj.size_bytes !== undefined ? Number(obj.size_bytes) : undefined,
  };
}

// =============================================================================
// 映射函数: EvidenceRef
// =============================================================================

/**
 * 将 JSON 映射为 EvidenceRef
 */
export function mapToEvidenceRef(data: unknown): EvidenceRef {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid EvidenceRef data');
  }

  const obj = data as Record<string, unknown>;

  return {
    issue_key: String(obj.issue_key ?? ''),
    source_locator: String(obj.source_locator ?? ''),
    content_hash: String(obj.content_hash ?? ''),
    tool_revision: String(obj.tool_revision ?? ''),
    timestamp: String(obj.timestamp ?? ''),
    kind: String(obj.kind ?? 'FILE'),
  };
}

// =============================================================================
// 映射函数: ArtifactManifest
// =============================================================================

/**
 * 将 JSON 映射为 ArtifactManifest
 */
export function mapToArtifactManifest(data: unknown): ArtifactManifest {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid ArtifactManifest data');
  }

  const obj = data as Record<string, unknown>;

  // 映射 artifacts 数组
  const artifactsData = obj.artifacts;
  const artifacts: ArtifactRef[] = [];
  if (Array.isArray(artifactsData)) {
    for (const item of artifactsData) {
      try {
        artifacts.push(mapToArtifactRef(item));
      } catch (e) {
        console.warn('Failed to map artifact:', item, e);
      }
    }
  }

  // 映射 evidence 数组
  const evidenceData = obj.evidence;
  const evidence: ArtifactRef[] = [];
  if (Array.isArray(evidenceData)) {
    for (const item of evidenceData) {
      try {
        evidence.push(mapToArtifactRef(item));
      } catch (e) {
        console.warn('Failed to map evidence item:', item, e);
      }
    }
  }

  // 映射 env
  const envData = obj.env;
  const env: Record<string, string> = {};
  if (envData && typeof envData === 'object') {
    for (const [key, value] of Object.entries(envData)) {
      env[key] = String(value);
    }
  }

  return {
    schema_version: String(obj.schema_version ?? 'runtime_interface_v0.1'),
    task_id: String(obj.task_id ?? ''),
    run_id: String(obj.run_id ?? ''),
    artifacts,
    evidence,
    env,
    created_at: String(obj.created_at ?? ''),
  };
}

// =============================================================================
// 映射函数: RunResult
// =============================================================================

/**
 * 将 JSON 映射为 RunResult
 */
export function mapToRunResult(data: unknown): RunResult {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid RunResult data');
  }

  const obj = data as Record<string, unknown>;

  // 映射 status
  const statusValue = String(obj.status ?? 'pending');
  const status: RunStatus = RUN_STATUS_MAP[statusValue] || 'pending';

  // 映射 evidence_refs 数组
  const evidenceRefsData = obj.evidence_refs;
  const evidence_refs: EvidenceRef[] = [];
  if (Array.isArray(evidenceRefsData)) {
    for (const item of evidenceRefsData) {
      try {
        evidence_refs.push(mapToEvidenceRef(item));
      } catch (e) {
        console.warn('Failed to map evidence_ref:', item, e);
      }
    }
  }

  // 映射 manifest (可选)
  let manifest: ArtifactManifest | undefined;
  if (obj.manifest && typeof obj.manifest === 'object') {
    try {
      manifest = mapToArtifactManifest(obj.manifest);
    } catch (e) {
      console.warn('Failed to map manifest:', obj.manifest, e);
    }
  }

  // 映射 executed_commands
  const executedCommandsData = obj.executed_commands;
  const executed_commands: string[] = [];
  if (Array.isArray(executedCommandsData)) {
    for (const cmd of executedCommandsData) {
      executed_commands.push(String(cmd));
    }
  }

  // 映射 output
  const outputData = obj.output;
  const output: Record<string, unknown> = {};
  if (outputData && typeof outputData === 'object') {
    Object.assign(output, outputData);
  }

  // 映射 error_details
  const errorDetailsData = obj.error_details;
  const error_details: Record<string, unknown> = {};
  if (errorDetailsData && typeof errorDetailsData === 'object') {
    Object.assign(error_details, errorDetailsData);
  }

  return {
    schema_version: String(obj.schema_version ?? 'runtime_interface_v0.1'),
    task_id: String(obj.task_id ?? ''),
    run_id: String(obj.run_id ?? ''),
    executor: String(obj.executor ?? ''),
    status,
    started_at: String(obj.started_at ?? ''),
    finished_at: String(obj.finished_at ?? ''),
    executed_commands,
    exit_code: obj.exit_code !== undefined ? Number(obj.exit_code) : undefined,
    output,
    summary: String(obj.summary ?? ''),
    evidence_refs,
    manifest,
    error_code: obj.error_code ? String(obj.error_code) : undefined,
    error_message: obj.error_message ? String(obj.error_message) : undefined,
    error_details: Object.keys(error_details).length > 0 ? error_details : undefined,
    contract_ref: obj.contract_ref ? String(obj.contract_ref) : undefined,
    permit_ref: obj.permit_ref ? String(obj.permit_ref) : undefined,
    receipt_ref: obj.receipt_ref ? String(obj.receipt_ref) : undefined,
  };
}

// =============================================================================
// 映射函数: MainChainStatus (从 RunResult 推导)
// =============================================================================

/**
 * 从 RunResult 推导主链状态
 *
 * 这是一个简化的映射，真实场景中可能需要从多个 gate decision 文件聚合
 */
export function mapToMainChainStatus(runResult: RunResult): MainChainStatus {
  // 默认步骤状态
  const defaultSteps: Record<MainChain, MainChainStepResult> = {
    permit: {
      step: 'permit',
      status: runResult.status === 'success' ? 'PASS' : 'PENDING',
    },
    pre_absorb_check: {
      step: 'pre_absorb_check',
      status: runResult.status === 'success' ? 'PASS' : 'PENDING',
    },
    absorb: {
      step: 'absorb',
      status: runResult.status === 'success' ? 'PASS' : 'FAIL',
      started_at: runResult.started_at,
      finished_at: runResult.finished_at,
      evidence_ref: runResult.evidence_refs[0]?.source_locator,
      error_message: runResult.error_message,
    },
    local_accept: {
      step: 'local_accept',
      status: runResult.status === 'success' ? 'PASS' : 'PENDING',
    },
    final_accept: {
      step: 'final_accept',
      status: runResult.status === 'success' ? 'PASS' : 'PENDING',
      gate_decision: runResult.status === 'success' ? 'ALLOW' : 'DENY',
    },
  };

  // 根据 run_result 的 executor 判断当前步骤
  let currentStep: MainChain = 'absorb';
  if (runResult.executor.includes('local_accept')) {
    currentStep = 'local_accept';
  } else if (runResult.executor.includes('final_accept')) {
    currentStep = 'final_accept';
  }

  // 推导最终 gate decision
  let finalGateDecision: GateDecision | undefined;
  if (runResult.status === 'success') {
    finalGateDecision = 'ALLOW';
  } else if (runResult.status === 'failure' || runResult.status === 'blocked') {
    finalGateDecision = 'DENY';
  }

  return {
    task_id: runResult.task_id,
    run_id: runResult.run_id,
    current_step: currentStep,
    steps: defaultSteps,
    overall_status: runResult.status,
    final_gate_decision: finalGateDecision,
  };
}

// 修复类型引用
type MainChain = MainChainStep;

// =============================================================================
// 加载函数: 从文件路径加载真实数据
// =============================================================================

/**
 * 从真实 JSON 文件加载 RunResult
 * 用于开发/测试环境
 *
 * @param jsonPath - JSON 文件路径 (相对于 docs/ 根目录)
 * @returns RunResult
 */
export async function loadRunResultFromJson(jsonPath: string): Promise<RunResult> {
  // 在真实场景中，这会是一个 API 调用
  // 例如: fetch(`/api/v1/run_result?path=${jsonPath}`)

  // 这里模拟一个加载过程
  const response = await fetch(jsonPath);
  if (!response.ok) {
    throw new Error(`Failed to load RunResult from ${jsonPath}: ${response.statusText}`);
  }

  const data = await response.json();
  return mapToRunResult(data);
}

/**
 * 从真实 JSON 文件加载 ArtifactManifest
 *
 * @param jsonPath - JSON 文件路径 (相对于 docs/ 根目录)
 * @returns ArtifactManifest
 */
export async function loadManifestFromJson(jsonPath: string): Promise<ArtifactManifest> {
  const response = await fetch(jsonPath);
  if (!response.ok) {
    throw new Error(`Failed to load ArtifactManifest from ${jsonPath}: ${response.statusText}`);
  }

  const data = await response.json();
  return mapToArtifactManifest(data);
}

// =============================================================================
// 验证函数
// =============================================================================

/**
 * 验证 RunResult 数据完整性
 */
export function validateRunResult(runResult: RunResult): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!runResult.task_id) errors.push('Missing task_id');
  if (!runResult.run_id) errors.push('Missing run_id');
  if (!runResult.executor) errors.push('Missing executor');
  if (!runResult.started_at) errors.push('Missing started_at');
  if (!runResult.finished_at) errors.push('Missing finished_at');

  // 验证时间戳顺序
  if (runResult.started_at && runResult.finished_at) {
    const started = new Date(runResult.started_at).getTime();
    const finished = new Date(runResult.finished_at).getTime();
    if (finished < started) errors.push('finished_at is before started_at');
  }

  // 失败时必须有错误信息
  if (runResult.status === 'failure' && !runResult.error_message) {
    errors.push('Missing error_message for failed result');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
