/**
 * Runtime Interface Types
 *
 * 前端类型定义，对应 core/runtime_interface.py 中的数据结构
 *
 * 来源: core/runtime_interface.py v0.1
 * 用途: TASK-MAIN-04B - 前端承接主链状态、证据入口和运行结果
 */

// =============================================================================
// 枚举定义
// =============================================================================

/**
 * 执行状态 - 对应 RunStatus
 */
export type RunStatus = 'pending' | 'running' | 'success' | 'failure' | 'blocked' | 'cancelled';

/**
 * 工件类型 - 对应 ArtifactKind
 */
export type ArtifactKind =
  | 'blueprint'           // 设计蓝图
  | 'contract'            // 合同文件
  | 'code'                // 代码变更
  | 'test'                // 测试报告
  | 'evidence'            // 证据文件
  | 'config'              // 配置文件
  | 'documentation'       // 文档
  | 'other';              // 其他

/**
 * Gate 决策状态
 */
export type GateDecision = 'ALLOW' | 'REQUIRES_CHANGES' | 'DENY';

// =============================================================================
// 核心数据结构
// =============================================================================

/**
 * 工件引用 - 对应 ArtifactRef
 */
export interface ArtifactRef {
  /** 相对路径 */
  path: string;
  /** 工件类型 */
  kind: ArtifactKind;
  /** SHA256 hash (可选) */
  content_hash?: string;
  /** 文件大小 (字节) */
  size_bytes?: number;
}

/**
 * 证据引用 - 对应 EvidenceRef
 */
export interface EvidenceRef {
  /** 问题/任务标识 */
  issue_key: string;
  /** 定位符 (路径/URL) */
  source_locator: string;
  /** 内容 hash */
  content_hash: string;
  /** 工具版本 */
  tool_revision: string;
  /** 时间戳 */
  timestamp: string;
  /** 证据类型: FILE|LOG|DIFF|SNIPPET|URL */
  kind: string;
}

/**
 * 工件清单 - 对应 ArtifactManifest
 */
export interface ArtifactManifest {
  /** schema 版本 */
  schema_version: string;
  /** 任务 ID */
  task_id: string;
  /** 运行 ID */
  run_id: string;
  /** 工件列表 */
  artifacts: ArtifactRef[];
  /** 证据列表 */
  evidence: ArtifactRef[];
  /** 环境信息 */
  env: Record<string, string>;
  /** 创建时间 */
  created_at: string;
}

/**
 * 执行结果 - 对应 RunResult
 */
export interface RunResult {
  /** schema 版本 */
  schema_version: string;
  /** 任务 ID */
  task_id: string;
  /** 运行 ID */
  run_id: string;
  /** 执行者 */
  executor: string;
  /** 执行状态 */
  status: RunStatus;
  /** 开始时间 */
  started_at: string;
  /** 完成时间 */
  finished_at: string;
  /** 执行的命令 */
  executed_commands?: string[];
  /** 退出码 */
  exit_code?: number;
  /** 输出数据 */
  output: Record<string, unknown>;
  /** 摘要 */
  summary: string;
  /** 证据引用列表 */
  evidence_refs: EvidenceRef[];
  /** 工件清单 */
  manifest?: ArtifactManifest;
  /** 错误码 (失败时) */
  error_code?: string;
  /** 错误消息 (失败时) */
  error_message?: string;
  /** 错误详情 (失败时) */
  error_details?: Record<string, unknown>;
  /** 合同引用 */
  contract_ref?: string;
  /** Permit 引用 */
  permit_ref?: string;
  /** 执行回执引用 */
  receipt_ref?: string;
}

// =============================================================================
// 主链步骤状态 (前端扩展)
// =============================================================================

/**
 * 主链步骤定义
 */
export type MainChainStep =
  | 'permit'              // Permit 检查
  | 'pre_absorb_check'    // absorb 前检查
  | 'absorb'              // absorb 执行
  | 'local_accept'        // 本地验收
  | 'final_accept';       // 最终验收

/**
 * 主链步骤状态
 */
export type MainChainStepStatus = 'PENDING' | 'IN_PROGRESS' | 'PASS' | 'FAIL' | 'SKIPPED';

/**
 * 主链步骤结果
 */
export interface MainChainStepResult {
  /** 步骤 ID */
  step: MainChainStep;
  /** 步骤状态 */
  status: MainChainStepStatus;
  /** Gate 决策 (如果有) */
  gate_decision?: GateDecision;
  /** 证据引用 */
  evidence_ref?: string;
  /** 错误消息 (失败时) */
  error_message?: string;
  /** 开始时间 */
  started_at?: string;
  /** 完成时间 */
  finished_at?: string;
}

/**
 * 完整主链状态
 */
export interface MainChainStatus {
  /** 任务 ID */
  task_id: string;
  /** 运行 ID */
  run_id: string;
  /** 当前步骤 */
  current_step: MainChainStep;
  /** 所有步骤结果 */
  steps: Record<MainChainStep, MainChainStepResult>;
  /** 整体状态 */
  overall_status: RunStatus;
  /** 最终 Gate 决策 */
  final_gate_decision?: GateDecision;
}

// =============================================================================
// 前端视图模型 (组合类型)
// =============================================================================

/**
 * 主链执行视图模型
 * 前端用于展示完整主链状态的组合类型
 */
export interface MainChainViewModel {
  /** 运行结果 */
  run_result: RunResult;
  /** 主链状态 */
  main_chain_status: MainChainStatus;
  /** 可用的证据入口 (从 run_result 和 manifest 聚合) */
  evidence_entries: EvidenceEntry[];
}

/**
 * 证据入口项
 * 前端用于展示证据的入口点
 */
export interface EvidenceEntry {
  /** 证据类型 */
  type: 'artifact' | 'evidence' | 'evidence_ref' | 'gate_decision' | 'manifest';
  /** 证据标题 */
  title: string;
  /** 证据路径/引用 */
  ref: string;
  /** 相关步骤 */
  related_step?: MainChainStep;
  /** 文件大小 (字节，可选) */
  size_bytes?: number;
  /** 内容 hash (可选) */
  content_hash?: string;
}

// =============================================================================
// 工具函数
// =============================================================================

/**
 * 判断运行状态是否为成功
 */
export function isRunSuccess(status: RunStatus): boolean {
  return status === 'success';
}

/**
 * 判断运行状态是否为失败
 */
export function isRunFailure(status: RunStatus): boolean {
  return status === 'failure';
}

/**
 * 判断 Gate 决策是否为通过
 */
export function isGateAllowed(decision: GateDecision | undefined): boolean {
  return decision === 'ALLOW';
}

/**
 * 获取步骤显示名称
 */
export function getStepDisplayName(step: MainChainStep): string {
  const stepNames: Record<MainChainStep, string> = {
    permit: 'Permit 检查',
    pre_absorb_check: 'Absorb 前检查',
    absorb: 'Absorb 执行',
    local_accept: '本地验收',
    final_accept: '最终验收',
  };
  return stepNames[step];
}

/**
 * 获取步骤状态颜色
 */
export function getStepStatusColor(status: MainChainStepStatus): string {
  const colors: Record<MainChainStepStatus, string> = {
    PENDING: '#9CA3AF',      // gray
    IN_PROGRESS: '#3B82F6',   // blue
    PASS: '#10B981',          // green
    FAIL: '#EF4444',          // red
    SKIPPED: '#F59E0B',       // amber
  };
  return colors[status];
}

/**
 * 从 RunResult 提取证据入口列表
 */
export function extractEvidenceEntries(runResult: RunResult): EvidenceEntry[] {
  const entries: EvidenceEntry[] = [];

  // 1. 添加 EvidenceRef 作为证据入口
  runResult.evidence_refs.forEach((ref, index) => {
    entries.push({
      type: 'evidence_ref',
      title: `证据引用 #${index + 1}`,
      ref: ref.source_locator,
      content_hash: ref.content_hash,
    });
  });

  // 2. 添加 manifest 中的 artifacts
  if (runResult.manifest) {
    runResult.manifest.artifacts.forEach((artifact) => {
      entries.push({
        type: 'artifact',
        title: `工件: ${artifact.path}`,
        ref: artifact.path,
        size_bytes: artifact.size_bytes,
        content_hash: artifact.content_hash,
      });
    });

    // 3. 添加 manifest 中的 evidence
    runResult.manifest.evidence.forEach((ev) => {
      entries.push({
        type: 'evidence',
        title: `证据: ${ev.path}`,
        ref: ev.path,
        size_bytes: ev.size_bytes,
        content_hash: ev.content_hash,
      });
    });

    // 4. 添加 manifest 本身作为证据入口
    entries.push({
      type: 'manifest',
      title: '工件清单 (manifest.json)',
      ref: `${runResult.task_id}/${runResult.run_id}/manifest.json`,
    });
  }

  return entries;
}
