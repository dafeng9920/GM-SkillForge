/**
 * Audit Detail Page - 裁决解释页
 *
 * This is the most important page in the system. It must function as:
 * - A ruling presentation page (not a normal error detail page)
 * - An audit workbench for understanding why an asset was passed/blocked
 * - An entry point for fixes and next actions
 *
 * Page Structure:
 * 1. Decision Header - Asset info, status, hashes, actions
 * 2. Decision Summary + Power Boundary - Conclusion first, then power boundaries
 * 3. 8 Gate Timeline - Gate-by-gate audit results
 * 4. EvidenceRef Panel - Evidence with visibility levels
 * 5. Issue Breakdown - Red Lines (blocking) vs Fixable Gaps (repairable)
 * 6. Governance Snapshot - Contract/Control + Hash/Reproducibility
 * 7. Footer Action Bar - Context-aware CTAs
 *
 * @module pages/governance/AuditDetailPage
 * @see docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md
 * @see docs/2026-03-12/verification/T-FE-05_frontend_mapping.md
 * @see docs/2026-03-12/verification/T-FE-06_visibility_and_permission_matrix.md
 */

import React, { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import type { ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import { useGovernanceCanvasSlot } from '../../components/governance/GovernanceCanvasSlot';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { INTENT_ROUTE_MAP, useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import { useGovernancePromptQuerySync } from '../../features/governanceInteraction/useGovernancePromptQuerySync';
import styles from './AuditDetailPage.module.css';

// ============================================
// Type Definitions (Layer 1/2 only - No Layer 3)
// ============================================

/**
 * Asset status enum -禁止使用 Success/Done/Approved
 * @see T-FE-03 Section 3.3 [1] Decision Header
 */
export type AssetStatus =
  | 'Draft'
  | 'In Audit'
  | 'Passed'
  | 'Fix Required'
  | 'Blocked'
  | 'Ready for Permit';

/**
 * Gate status enum
 * @see T-FE-03 Section 3.3 [4] 8 Gate Timeline
 */
export type GateStatus = 'Pass' | 'Fail' | 'Warn' | 'Skip';

/**
 * Evidence visibility levels - MUST be enforced
 * @see T-FE-03 Section 3.3 [5] EvidenceRef Panel
 * @see T-FE-06 Section 3.5.2 EvidenceRef visibility
 */
export type EvidenceVisibility = 'visible' | 'summary-only' | 'restricted';

/**
 * Impact level for red lines
 */
export type ImpactLevel = 'CRITICAL' | 'HIGH';

/**
 * Severity level for fixable gaps
 */
export type SeverityLevel = 'Low' | 'Medium' | 'High';

/**
 * Evidence reference structure (Layer 2)
 * - Never includes full content when visibility=restricted
 * - API must filter Layer 3 fields before sending
 */
export interface EvidenceRef {
  id: string; // E.g., EVD-003
  source_type: 'Log' | 'File' | 'Metric' | 'Snapshot';
  summary: string;
  strength: 'Weak' | 'Medium' | 'Strong';
  visibility: EvidenceVisibility;
  linked_gate: string;
  // Layer 3 fields NEVER included here:
  // - collection_method, source_probe_info, weight_calculation, etc.
}

/**
 * Gate result structure (Layer 1/2)
 * - Never includes rule thresholds, weights, or probe details
 */
export interface GateResult {
  gate_name: string; // E.g., "Boundary Integrity"
  gate_number: number; // 1-8
  status: GateStatus;
  reason: string;
  triggered_rules: string[]; // Rule refs only - E.g., RULE-4.2, RULE-4.7
  evidence_count: number;
  evidence_refs?: EvidenceRef[];
  fix_suggestion?: string;
  // Layer 3 fields NEVER included:
  // - rule_threshold, rule_weight, rule_expression, probe_code, etc.
}

/**
 * Red line issue (blocking)
 */
export interface RedLineIssue {
  issue_title: string;
  impact: ImpactLevel;
  triggered_gate: string;
  rules: string[]; // Rule refs only
  why_blocking: string;
  required_disposition: string;
}

/**
 * Fixable gap (repairable)
 */
export interface FixableGap {
  gap_title: string;
  severity: SeverityLevel;
  related_gate: string;
  suggested_fix: string;
  expected_outcome: string;
}

/**
 * Contract/Control snapshot
 */
export interface ContractControlSnapshot {
  contract_summary: string;
  constitution_version: string; // E.g., v2.1
  rule_pack_version: string; // E.g., v1.0.3
  control_spec_version: string; // E.g., v3.5
  linked_manifest: string;
  audit_scope: string;
}

/**
 * Hash binding structure
 */
export interface HashBinding {
  demand_hash: string;
  contract_hash: string;
  decision_hash: string;
  revision_lineage: string;
  linked_manifest_id: string;
}

/**
 * Audit detail data (Layer 1/2)
 * @see T-FE-03 Section 3.2 Page Skeleton
 */
export interface AuditDetailData {
  // Decision Header fields
  asset_name: string;
  asset_type: 'Skill' | 'Workflow' | 'Agent Asset';
  revision_id: string; // E.g., R-014
  current_status: AssetStatus;
  audit_version: string; // E.g., v1.0
  decision_hash: string;
  audited_at: string;
  owner?: string;
  reviewer?: string;

  // Decision Summary
  final_decision: 'Passed' | 'Blocked' | 'Fix Required';
  primary_reason: string;
  evidence_sufficiency: 'Sufficient for approval' | 'Sufficient for rejection' | 'Insufficient';
  permit_readiness: string;
  critical_issues_count: number;
  fixable_gaps_count: number;
  evidence_ref_count: number;

  // 8 Gate Results
  gate_results: GateResult[];

  // Issues
  red_lines: RedLineIssue[];
  fixable_gaps: FixableGap[];

  // Governance Snapshot
  contract_control: ContractControlSnapshot;
  hash_binding: HashBinding;
}

const PAGE_COPY = {
  zh: {
    breadcrumbRegistry: '登记',
    type: '类型',
    revision: '修订',
    auditVersion: '审计版本',
    owner: '负责人',
    reviewer: '审查者',
    auditedAt: '审计时间',
    reviewGaps: '审查缺口',
    exportAuditPack: '导出 AuditPack',
    rerunAudit: '重新审计',
    submitForPermit: '提交 Permit',
    finalDecision: '最终裁决',
    primaryReason: '主要原因',
    evidenceSufficiency: '证据充分性',
    permitReadiness: 'Permit 就绪度',
    critical: '关键项',
    fixable: '可修复',
    evidence: '证据',
    powerBoundary: '权限边界',
    executionCanRun: '✓ 可以执行',
    executionCanOutput: '✓ 可以产出输出物',
    executionCannotApprove: '✗ 不能批准发布',
    auditCanInspect: '✓ 可以检查',
    auditCanDecide: '✓ 可以给出审计裁决',
    auditCannotPermit: '✗ 不能签发 Permit',
    complianceCanPermit: '✓ 可以签发 Permit',
    complianceCanCondition: '✓ 可以附加条件',
    complianceCannotModify: '✗ 不能修改执行输出',
    gateTimeline: '8 Gate 时间线',
    reason: '原因',
    triggeredRules: '触发规则',
    ruleRefsOnly: '（仅显示规则引用，不暴露规则细节）',
    evidenceLinked: '条证据已关联',
    fixSuggestion: '修复建议',
    evidenceReference: '证据引用',
    evidenceItems: '条证据',
    permissionRequired: '🔒 需要额外权限',
    restrictedMessage: '完整内容需要更高授权。',
    redLinesTitle: '红线（阻断问题）',
    redLinesDesc: '这些问题必须解决后，资产才能继续进入下一步。',
    noCriticalIssues: '未发现关键阻断问题。',
    triggeredGate: '触发 Gate',
    rules: '规则',
    whyBlocking: '阻断原因',
    requiredDisposition: '必须处置',
    fixableGapsTitle: '可修复缺口',
    fixableGapsDesc: '这些问题可以修复，并在之后重新提交审计。',
    noFixableGaps: '未发现可修复缺口。',
    relatedGate: '关联 Gate',
    suggestedFix: '建议修复',
    expectedOutcome: '预期结果',
    contractControlSnapshot: 'Contract / Control 快照',
    contractSummary: 'Contract 摘要',
    constitutionVersion: 'Constitution 版本',
    rulePackVersion: 'Rule Pack 版本',
    controlSpecVersion: 'ControlSpec 版本',
    linkedManifest: '关联 Manifest',
    auditScope: '审计范围',
    hashRepro: 'Hash 与可复现性',
    revisionLineage: '修订谱系',
    linkedManifestId: '关联 Manifest ID',
    bindingNotice: '该裁决绑定到当前修订与策略上下文。任何修订或策略变化都会使本次审计结果失效。',
    blockedAction1: '查看关键修复',
    blockedAction2: '导出修复摘要',
    blockedAction3: '修复后重跑',
    fixAction1: '进入缺口分析',
    fixAction2: '指派负责人',
    fixAction3: '重新提交审计',
    passedAction1: '导出 AuditPack',
    passedAction2: '提交 Permit',
    readyAction1: '打开 Permit 草稿',
    readyAction2: '签发 Permit',
    copyAria: '复制',
    statuses: {
      Draft: '草稿',
      'In Audit': '审计中',
      Passed: '通过',
      'Fix Required': '需要修复',
      Blocked: '已阻断',
      'Ready for Permit': '可申请 Permit',
      Pass: '通过',
      Fail: '失败',
      Warn: '警告',
      Skip: '跳过',
    },
  },
  en: {
    breadcrumbRegistry: 'Registry',
    type: 'Type',
    revision: 'Revision',
    auditVersion: 'Audit Version',
    owner: 'Owner',
    reviewer: 'Reviewer',
    auditedAt: 'Audited at',
    reviewGaps: 'Review Gaps',
    exportAuditPack: 'Export AuditPack',
    rerunAudit: 'Re-run Audit',
    submitForPermit: 'Submit for Permit',
    finalDecision: 'Final Decision',
    primaryReason: 'Primary Reason',
    evidenceSufficiency: 'Evidence Sufficiency',
    permitReadiness: 'Permit Readiness',
    critical: 'Critical',
    fixable: 'Fixable',
    evidence: 'Evidence',
    powerBoundary: 'Power Boundary',
    executionCanRun: '✓ Can run',
    executionCanOutput: '✓ Can produce outputs',
    executionCannotApprove: '✗ Cannot approve release',
    auditCanInspect: '✓ Can inspect',
    auditCanDecide: '✓ Can issue audit decision',
    auditCannotPermit: '✗ Cannot issue permit',
    complianceCanPermit: '✓ Can issue permit',
    complianceCanCondition: '✓ Can define conditions',
    complianceCannotModify: '✗ Cannot modify execution output',
    gateTimeline: '8 Gate Timeline',
    reason: 'Reason',
    triggeredRules: 'Triggered Rules',
    ruleRefsOnly: '(Rule references only - details not exposed)',
    evidenceLinked: 'evidence item(s) linked',
    fixSuggestion: 'Fix Suggestion',
    evidenceReference: 'Evidence Reference',
    evidenceItems: 'evidence item(s)',
    permissionRequired: '🔒 Permission Required',
    restrictedMessage: 'Full content requires additional authorization.',
    redLinesTitle: 'Red Lines (Blocking Issues)',
    redLinesDesc: 'These issues MUST be resolved before the asset can proceed.',
    noCriticalIssues: 'No critical blocking issues detected.',
    triggeredGate: 'Triggered Gate',
    rules: 'Rules',
    whyBlocking: 'Why Blocking',
    requiredDisposition: 'Required Disposition',
    fixableGapsTitle: 'Fixable Gaps (Repairable Issues)',
    fixableGapsDesc: 'These issues can be fixed and the asset resubmitted for audit.',
    noFixableGaps: 'No fixable gaps detected.',
    relatedGate: 'Related Gate',
    suggestedFix: 'Suggested Fix',
    expectedOutcome: 'Expected Outcome',
    contractControlSnapshot: 'Contract / Control Snapshot',
    contractSummary: 'Contract Summary',
    constitutionVersion: 'Constitution Version',
    rulePackVersion: 'Rule Pack Version',
    controlSpecVersion: 'ControlSpec Version',
    linkedManifest: 'Linked Manifest',
    auditScope: 'Audit Scope',
    hashRepro: 'Hash & Reproducibility',
    revisionLineage: 'Revision Lineage',
    linkedManifestId: 'Linked Manifest ID',
    bindingNotice: 'This decision is bound to the current revision and policy context. Any change in revision or policy context will invalidate this audit result.',
    blockedAction1: 'View Critical Fixes',
    blockedAction2: 'Export Fix Brief',
    blockedAction3: 'Re-run After Changes',
    fixAction1: 'Go to Gap Analysis',
    fixAction2: 'Assign Owner',
    fixAction3: 'Re-submit to Audit',
    passedAction1: 'Export AuditPack',
    passedAction2: 'Submit for Permit',
    readyAction1: 'Open Permit Draft',
    readyAction2: 'Issue Permit',
    copyAria: 'Copy',
    statuses: {
      Draft: 'Draft',
      'In Audit': 'In Audit',
      Passed: 'Passed',
      'Fix Required': 'Fix Required',
      Blocked: 'Blocked',
      'Ready for Permit': 'Ready for Permit',
      Pass: 'Pass',
      Fail: 'Fail',
      Warn: 'Warn',
      Skip: 'Skip',
    },
  },
} as const;

// ============================================
// Sub-Components (Page-Scoped, Not Shared)
// ============================================

/**
 * StatusLabel - Consistent status display
 * 禁止使用: Success/Done/Approved/Live
 */
const StatusLabel: React.FC<{
  status: AssetStatus | GateStatus;
  variant?: 'default' | 'critical' | 'success';
}> = ({ status, variant = 'default' }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const getVariantClass = () => {
    if (variant === 'critical') return styles['status-critical'];
    if (variant === 'success') return styles['status-success'];
    return styles['status-default'];
  };

  return (
    <span className={`${styles['status-label']} ${getVariantClass()}`}>
      {copy.statuses[status]}
    </span>
  );
};

/**
 * HashDisplay - Consistent hash display
 * Format: first 8 chars + ellipsis, hover for full
 */
const HashDisplay: React.FC<{
  label: string;
  value: string;
}> = ({ label, value }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  }, [value]);

  const shortHash = value.length > 12 ? `${value.slice(0, 12)}...` : value;

  return (
    <div className={styles['hash-display']}>
      <span className={styles['hash-label']}>{label}:</span>
      <span className={styles['hash-value']} title={value}>
        {shortHash}
      </span>
      <button
        className={styles['hash-copy-btn']}
        onClick={handleCopy}
        aria-label={`${copy.copyAria} ${label}`}
      >
        {copied ? '✓' : '📋'}
      </button>
    </div>
  );
};

/**
 * DecisionHeader - [1] Page header with asset info and status
 */
const DecisionHeader: React.FC<{
  data: AuditDetailData;
}> = ({ data }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const navigate = useNavigate();

  const handleExportAuditPack = useCallback(() => {
    // TODO: Implement export functionality
    console.log('Export AuditPack clicked');
  }, []);

  const handleReRunAudit = useCallback(() => {
    // TODO: Implement re-run functionality
    console.log('Re-run Audit clicked');
  }, []);

  const handleSubmitForPermit = useCallback(() => {
    // Navigate to permit page
    navigate('/permit');
  }, [navigate]);

  return (
    <header className={styles['decision-header']}>
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Breadcrumb">
        <span>{copy.breadcrumbRegistry}</span>
        <span className={styles.separator}>/</span>
        <span>{data.asset_name}</span>
        <span className={styles.separator}>/</span>
        <span className={styles['revision-id']}>{data.revision_id}</span>
      </nav>

      {/* Main header content */}
      <div className={styles['header-main']}>
        <div className={styles['header-title-row']}>
          <h1 className={styles['page-title']}>{data.asset_name}</h1>
          <StatusLabel
            status={data.current_status}
            variant={data.current_status === 'Blocked' ? 'critical' : 'default'}
          />
        </div>

        <div className={styles['header-meta']}>
          <div className={styles['meta-item']}>
              <span className={styles['meta-label']}>{copy.type}:</span>
            <span className={styles['meta-value']}>{data.asset_type}</span>
          </div>
          <div className={styles['meta-item']}>
              <span className={styles['meta-label']}>{copy.revision}:</span>
            <span className={styles['meta-value']}>{data.revision_id}</span>
          </div>
          <div className={styles['meta-item']}>
              <span className={styles['meta-label']}>{copy.auditVersion}:</span>
            <span className={styles['meta-value']}>{data.audit_version}</span>
          </div>
          {data.owner && (
            <div className={styles['meta-item']}>
              <span className={styles['meta-label']}>{copy.owner}:</span>
              <span className={styles['meta-value']}>{data.owner}</span>
            </div>
          )}
          {data.reviewer && (
            <div className={styles['meta-item']}>
              <span className={styles['meta-label']}>{copy.reviewer}:</span>
              <span className={styles['meta-value']}>{data.reviewer}</span>
            </div>
          )}
        </div>
      </div>

      {/* Decision hash */}
      <div className={styles['decision-hash-row']}>
        <HashDisplay label="decision_hash" value={data.decision_hash} />
        <span className={styles['audited-at']}>
          {copy.auditedAt}: {new Date(data.audited_at).toLocaleString()}
        </span>
      </div>

      {/* Header actions */}
      <div className={styles['header-actions']}>
        <button className={styles['btn-secondary']}>{copy.reviewGaps}</button>
        <button className={styles['btn-secondary']} onClick={handleExportAuditPack}>
          {copy.exportAuditPack}
        </button>
        <button className={styles['btn-secondary']} onClick={handleReRunAudit}>
          {copy.rerunAudit}
        </button>
        {data.current_status === 'Passed' && (
          <button className={styles['btn-primary']} onClick={handleSubmitForPermit}>
            {copy.submitForPermit}
          </button>
        )}
      </div>
    </header>
  );
};

/**
 * DecisionSummaryCard - [2] Conclusion-first summary
 */
const DecisionSummaryCard: React.FC<{
  data: AuditDetailData;
}> = ({ data }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const getStatusClass = () => {
    if (data.final_decision === 'Passed') return styles['summary-passed'];
    if (data.final_decision === 'Blocked') return styles['summary-blocked'];
    return styles['summary-warning'];
  };

  return (
    <section className={`${styles['decision-summary']} ${getStatusClass()}`}>
      <h2 className={styles['summary-title']}>{copy.finalDecision}</h2>

      <div className={styles['summary-decision']}>
        <span className={styles['decision-text']}>{data.final_decision}</span>
      </div>

      <div className={styles['summary-section']}>
        <h3 className={styles['summary-section-title']}>{copy.primaryReason}</h3>
        <p className={styles['summary-section-content']}>{data.primary_reason}</p>
      </div>

      <div className={styles['summary-section']}>
        <h3 className={styles['summary-section-title']}>{copy.evidenceSufficiency}</h3>
        <p className={styles['summary-section-content']}>{data.evidence_sufficiency}</p>
      </div>

      <div className={styles['summary-section']}>
        <h3 className={styles['summary-section-title']}>{copy.permitReadiness}</h3>
        <p className={styles['summary-section-content']}>{data.permit_readiness}</p>
      </div>

      <div className={styles['summary-tags']}>
        <div className={styles['summary-tag']}>
          <span className={styles['tag-value']}>{data.critical_issues_count}</span>
          <span className={styles['tag-label']}>{copy.critical}</span>
        </div>
        <div className={styles['summary-tag']}>
          <span className={styles['tag-value']}>{data.fixable_gaps_count}</span>
          <span className={styles['tag-label']}>{copy.fixable}</span>
        </div>
        <div className={styles['summary-tag']}>
          <span className={styles['tag-value']}>{data.evidence_ref_count}</span>
          <span className={styles['tag-label']}>{copy.evidence}</span>
        </div>
      </div>
    </section>
  );
};

/**
 * PowerBoundaryCard - [3] 三权分立边界展示
 */
const PowerBoundaryCard: React.FC = () => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  return (
    <section className={styles['power-boundary']}>
      <h2 className={styles['power-boundary-title']}>{copy.powerBoundary}</h2>

      <div className={styles['power-boundary-grid']}>
        {/* Execution Column */}
        <div className={styles['power-column']}>
          <h3 className={styles['power-column-title']}>Execution</h3>
          <ul className={styles['power-list']}>
            <li className={styles['power-item-allowed']}>{copy.executionCanRun}</li>
            <li className={styles['power-item-allowed']}>{copy.executionCanOutput}</li>
            <li className={styles['power-item-denied']}>{copy.executionCannotApprove}</li>
          </ul>
        </div>

        {/* Audit Column */}
        <div className={styles['power-column']}>
          <h3 className={styles['power-column-title']}>Audit</h3>
          <ul className={styles['power-list']}>
            <li className={styles['power-item-allowed']}>{copy.auditCanInspect}</li>
            <li className={styles['power-item-allowed']}>{copy.auditCanDecide}</li>
            <li className={styles['power-item-denied']}>{copy.auditCannotPermit}</li>
          </ul>
        </div>

        {/* Compliance Column */}
        <div className={styles['power-column']}>
          <h3 className={styles['power-column-title']}>Compliance</h3>
          <ul className={styles['power-list']}>
            <li className={styles['power-item-allowed']}>{copy.complianceCanPermit}</li>
            <li className={styles['power-item-allowed']}>{copy.complianceCanCondition}</li>
            <li className={styles['power-item-denied']}>{copy.complianceCannotModify}</li>
          </ul>
        </div>
      </div>
    </section>
  );
};

/**
 * GateCard - Individual gate result display
 * NEVER includes Layer 3: threshold, weight, rule_expression, probe_code
 */
const GateCard: React.FC<{
  gate: GateResult;
}> = ({ gate }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const getStatusVariant = (): 'default' | 'critical' | 'success' => {
    if (gate.status === 'Pass') return 'success';
    if (gate.status === 'Fail') return 'critical';
    return 'default';
  };

  return (
    <article className={styles['gate-card']}>
      <header className={styles['gate-header']}>
        <h3 className={styles['gate-title']}>
          Gate {gate.gate_number} — {gate.gate_name}
        </h3>
        <StatusLabel status={gate.status} variant={getStatusVariant()} />
      </header>

      {gate.reason && (
        <div className={styles['gate-section']}>
          <h4 className={styles['gate-section-title']}>{copy.reason}</h4>
          <p className={styles['gate-section-content']}>{gate.reason}</p>
        </div>
      )}

      {gate.triggered_rules.length > 0 && (
        <div className={styles['gate-section']}>
          <h4 className={styles['gate-section-title']}>{copy.triggeredRules}</h4>
          <ul className={styles['rule-list']}>
            {gate.triggered_rules.map((rule) => (
              <li key={rule} className={styles['rule-ref']}>
                {rule}
              </li>
            ))}
          </ul>
          <p className={styles['rule-note']}>
            {copy.ruleRefsOnly}
          </p>
        </div>
      )}

      {gate.evidence_count > 0 && (
        <div className={styles['gate-section']}>
          <h4 className={styles['gate-section-title']}>{copy.evidence}</h4>
          <p className={styles['gate-section-content']}>
            {gate.evidence_count} {copy.evidenceLinked}
          </p>
        </div>
      )}

      {gate.fix_suggestion && (
        <div className={styles['gate-section']}>
          <h4 className={styles['gate-section-title']}>{copy.fixSuggestion}</h4>
          <p className={styles['gate-section-content']}>{gate.fix_suggestion}</p>
        </div>
      )}
    </article>
  );
};

/**
 * GateTimelineCard - [4] 8 Gate Timeline
 */
const GateTimelineCard: React.FC<{
  gates: GateResult[];
}> = ({ gates }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  return (
    <section className={styles['gate-timeline']}>
      <h2 className={styles['section-title']}>{copy.gateTimeline}</h2>
      <div className={styles['gate-list']}>
        {gates.map((gate) => (
          <GateCard key={gate.gate_number} gate={gate} />
        ))}
      </div>
    </section>
  );
};

/**
 * EvidenceRefPanel - [5] Evidence reference panel
 * Enforces visibility levels: visible / summary-only / restricted
 */
const EvidenceRefPanel: React.FC<{
  evidenceRefs: EvidenceRef[];
}> = ({ evidenceRefs }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRef | null>(null);

  return (
    <aside className={styles['evidence-panel']}>
      <h2 className={styles['section-title']}>{copy.evidenceReference}</h2>
      <p className={styles['section-subtitle']}>
        {evidenceRefs.length} {copy.evidenceItems}
      </p>

      <div className={styles['evidence-list']}>
        {evidenceRefs.map((evidence) => {
          const visibilityClass = styles[`evidence-${evidence.visibility}`];

          return (
            <div
              key={evidence.id}
              className={`${styles['evidence-item']} ${visibilityClass}`}
              onClick={() => setSelectedEvidence(evidence)}
            >
              <div className={styles['evidence-header']}>
                <span className={styles['evidence-id']}>{evidence.id}</span>
                <span className={styles['evidence-source']}>{evidence.source_type}</span>
              </div>
              <p className={styles['evidence-summary']}>{evidence.summary}</p>
              <div className={styles['evidence-footer']}>
                <span className={styles['evidence-strength']}>{evidence.strength}</span>
                <span className={styles['evidence-visibility']}>{evidence.visibility}</span>
                <span className={styles['evidence-gate']}>{evidence.linked_gate}</span>
              </div>
              {evidence.visibility === 'restricted' && (
                <div className={styles['restricted-badge']}>
                  {copy.permissionRequired}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedEvidence && (
        <div className={styles['evidence-detail']}>
          <button
            className={styles['close-btn']}
            onClick={() => setSelectedEvidence(null)}
          >
            ✕
          </button>
          <h3>{selectedEvidence.id}</h3>
          <p>{selectedEvidence.summary}</p>
          {selectedEvidence.visibility === 'restricted' && (
            <p className={styles['restricted-message']}>
              {copy.restrictedMessage}
            </p>
          )}
        </div>
      )}
    </aside>
  );
};

/**
 * RedLinesCard - [6a] Red Lines (blocking issues)
 */
const RedLinesCard: React.FC<{
  redLines: RedLineIssue[];
}> = ({ redLines }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  if (redLines.length === 0) {
    return (
      <section className={styles['red-lines']}>
        <h2 className={styles['section-title']}>{copy.redLinesTitle}</h2>
        <p className={styles['empty-message']}>{copy.noCriticalIssues}</p>
      </section>
    );
  }

  return (
    <section className={styles['red-lines']}>
      <h2 className={styles['section-title-with-icon']}>
        <span className={styles['warning-icon']}>⚠</span>
        {copy.redLinesTitle}
      </h2>
      <p className={styles['section-description']}>
        {copy.redLinesDesc}
      </p>

      <div className={styles['issue-list']}>
        {redLines.map((issue, index) => (
          <article key={index} className={styles['red-line-item']}>
            <div className={styles['issue-header']}>
              <h3 className={styles['issue-title']}>{issue.issue_title}</h3>
              <span className={`${styles['impact-badge']} ${styles[`impact-${issue.impact.toLowerCase()}`]}`}>
                {issue.impact}
              </span>
            </div>

            <div className={styles['issue-field']}>
              <span className={styles['issue-label']}>{copy.triggeredGate}:</span>
              <span className={styles['issue-value']}>{issue.triggered_gate}</span>
            </div>

            {issue.rules.length > 0 && (
              <div className={styles['issue-field']}>
                <span className={styles['issue-label']}>{copy.rules}:</span>
                <div className={styles['issue-rules']}>
                  {issue.rules.map((rule) => (
                    <span key={rule} className={styles['rule-ref-small']}>
                      {rule}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className={styles['issue-field']}>
              <span className={styles['issue-label']}>{copy.whyBlocking}:</span>
              <p className={styles['issue-description']}>{issue.why_blocking}</p>
            </div>

            <div className={styles['issue-field']}>
              <span className={styles['issue-label']}>{copy.requiredDisposition}:</span>
              <p className={styles['issue-description']}>{issue.required_disposition}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};

/**
 * FixableGapsCard - [6b] Fixable Gaps (repairable issues)
 */
const FixableGapsCard: React.FC<{
  gaps: FixableGap[];
}> = ({ gaps }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  if (gaps.length === 0) {
    return (
      <section className={styles['fixable-gaps']}>
        <h2 className={styles['section-title']}>{copy.fixableGapsTitle}</h2>
        <p className={styles['empty-message']}>{copy.noFixableGaps}</p>
      </section>
    );
  }

  return (
    <section className={styles['fixable-gaps']}>
      <h2 className={styles['section-title-with-icon']}>
        <span className={styles['fix-icon']}>🔧</span>
        {copy.fixableGapsTitle}
      </h2>
      <p className={styles['section-description']}>
        {copy.fixableGapsDesc}
      </p>

      <div className={styles['gap-list']}>
        {gaps.map((gap, index) => (
          <article key={index} className={styles['gap-item']}>
            <div className={styles['gap-header']}>
              <h3 className={styles['gap-title']}>{gap.gap_title}</h3>
              <span className={`${styles['severity-badge']} ${styles[`severity-${gap.severity.toLowerCase()}`]}`}>
                {gap.severity}
              </span>
            </div>

            <div className={styles['gap-field']}>
              <span className={styles['gap-label']}>{copy.relatedGate}:</span>
              <span className={styles['gap-value']}>{gap.related_gate}</span>
            </div>

            <div className={styles['gap-field']}>
              <span className={styles['gap-label']}>{copy.suggestedFix}:</span>
              <p className={styles['gap-description']}>{gap.suggested_fix}</p>
            </div>

            <div className={styles['gap-field']}>
              <span className={styles['gap-label']}>{copy.expectedOutcome}:</span>
              <p className={styles['gap-description']}>{gap.expected_outcome}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};

/**
 * IssueBreakdownRow - [6] Red Lines + Fixable Gaps side by side
 */
const IssueBreakdownRow: React.FC<{
  redLines: RedLineIssue[];
  fixableGaps: FixableGap[];
}> = ({ redLines, fixableGaps }) => {
  return (
    <section className={styles['issue-breakdown']}>
      <RedLinesCard redLines={redLines} />
      <FixableGapsCard gaps={fixableGaps} />
    </section>
  );
};

/**
 * ContractControlSnapshotCard - [7a] Contract/Control snapshot
 */
const ContractControlSnapshotCard: React.FC<{
  snapshot: ContractControlSnapshot;
}> = ({ snapshot }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  return (
    <section className={styles['contract-control']}>
      <h2 className={styles['section-title']}>{copy.contractControlSnapshot}</h2>

      <div className={styles['contract-content']}>
        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.contractSummary}</span>
          <p className={styles['contract-value']}>{snapshot.contract_summary}</p>
        </div>

        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.constitutionVersion}</span>
          <span className={styles['contract-value-mono']}>{snapshot.constitution_version}</span>
        </div>

        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.rulePackVersion}</span>
          <span className={styles['contract-value-mono']}>{snapshot.rule_pack_version}</span>
        </div>

        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.controlSpecVersion}</span>
          <span className={styles['contract-value-mono']}>{snapshot.control_spec_version}</span>
        </div>

        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.linkedManifest}</span>
          <span className={styles['contract-value-mono']}>{snapshot.linked_manifest}</span>
        </div>

        <div className={styles['contract-field']}>
          <span className={styles['contract-label']}>{copy.auditScope}</span>
          <span className={styles['contract-value']}>{snapshot.audit_scope}</span>
        </div>
      </div>
    </section>
  );
};

/**
 * HashReproducibilityCard - [7b] Hash & Reproducibility
 */
const HashReproducibilityCard: React.FC<{
  hashBinding: HashBinding;
}> = ({ hashBinding }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  return (
    <section className={styles['hash-reproducibility']}>
      <h2 className={styles['section-title']}>{copy.hashRepro}</h2>

      <div className={styles['hash-list']}>
        <HashDisplay label="demand_hash" value={hashBinding.demand_hash} />
        <HashDisplay label="contract_hash" value={hashBinding.contract_hash} />
        <HashDisplay label="decision_hash" value={hashBinding.decision_hash} />
      </div>

      <div className={styles['hash-field']}>
        <span className={styles['hash-label']}>{copy.revisionLineage}</span>
        <span className={styles['hash-value']}>{hashBinding.revision_lineage}</span>
      </div>

      <div className={styles['hash-field']}>
        <span className={styles['hash-label']}>{copy.linkedManifestId}</span>
        <span className={styles['hash-value-mono']}>{hashBinding.linked_manifest_id}</span>
      </div>

      <p className={styles['binding-notice']}>
        {copy.bindingNotice}
      </p>
    </section>
  );
};

/**
 * GovernanceSnapshotRow - [7] Contract/Control + Hash/Reproducibility
 */
const GovernanceSnapshotRow: React.FC<{
  contractControl: ContractControlSnapshot;
  hashBinding: HashBinding;
}> = ({ contractControl, hashBinding }) => {
  return (
    <section className={styles['governance-snapshot']}>
      <ContractControlSnapshotCard snapshot={contractControl} />
      <HashReproducibilityCard hashBinding={hashBinding} />
    </section>
  );
};

/**
 * FooterActionBar - [8] Context-aware action bar
 */
const FooterActionBar: React.FC<{
  status: AssetStatus;
}> = ({ status }) => {
  const { language } = useLanguage();
  const copy = PAGE_COPY[language];
  const navigate = useNavigate();
  type FooterAction = {
    label: string;
    primary: boolean;
    onClick?: () => void;
  };

  const getActionsForStatus = (): FooterAction[] => {
    switch (status) {
      case 'Blocked':
        return [
          { label: copy.blockedAction1, primary: false },
          { label: copy.blockedAction2, primary: false },
          { label: copy.blockedAction3, primary: true },
        ];
      case 'Fix Required':
        return [
          { label: copy.fixAction1, primary: false },
          { label: copy.fixAction2, primary: false },
          { label: copy.fixAction3, primary: true },
        ];
      case 'Passed':
        return [
          { label: copy.passedAction1, primary: false },
          { label: copy.passedAction2, primary: true, onClick: () => navigate('/permit') },
        ];
      case 'Ready for Permit':
        return [
          { label: copy.readyAction1, primary: false },
          { label: copy.readyAction2, primary: true, onClick: () => navigate('/permit') },
        ];
      default:
        return [];
    }
  };

  const actions = getActionsForStatus();

  if (actions.length === 0) return null;

  return (
    <footer className={styles['footer-action-bar']}>
      {actions.map((action, index) => (
        <button
          key={index}
          className={action.primary ? styles['btn-primary'] : styles['btn-secondary']}
          onClick={action.onClick}
        >
          {action.label}
        </button>
      ))}
    </footer>
  );
};

// ============================================
// Mock Data (TODO: Replace with API calls)
// ============================================

const mockAuditData: AuditDetailData = {
  // Decision Header
  asset_name: 'Payment Agent Skill',
  asset_type: 'Skill',
  revision_id: 'R-014',
  current_status: 'Blocked',
  audit_version: 'v1.0',
  decision_hash: 'sha256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4',
  audited_at: '2026-03-12T10:30:00Z',
  owner: 'Execution Team',
  reviewer: 'Antigravity-2',

  // Decision Summary
  final_decision: 'Blocked',
  primary_reason: 'Execution boundary leakage detected under Gate 4.',
  evidence_sufficiency: 'Sufficient for rejection',
  permit_readiness: 'Not eligible until critical gaps are resolved',
  critical_issues_count: 2,
  fixable_gaps_count: 4,
  evidence_ref_count: 11,

  // 8 Gate Results
  gate_results: [
    {
      gate_name: 'Identity & Declaration',
      gate_number: 1,
      status: 'Pass',
      reason: 'Asset identity and declaration are properly defined.',
      triggered_rules: [],
      evidence_count: 2,
    },
    {
      gate_name: 'Control Specification',
      gate_number: 2,
      status: 'Pass',
      reason: 'Control specification meets requirements.',
      triggered_rules: [],
      evidence_count: 1,
    },
    {
      gate_name: 'Evidence Completeness',
      gate_number: 3,
      status: 'Pass',
      reason: 'Required evidence artifacts are present.',
      triggered_rules: [],
      evidence_count: 3,
    },
    {
      gate_name: 'Boundary Integrity',
      gate_number: 4,
      status: 'Fail',
      reason: 'Execution logic exceeded declared control scope.',
      triggered_rules: ['RULE-4.2', 'RULE-4.7'],
      evidence_count: 2,
      fix_suggestion: 'Tighten declared control boundaries and update ControlSpec.',
    },
    {
      gate_name: 'Resource Constraints',
      gate_number: 5,
      status: 'Pass',
      reason: 'Resource usage within acceptable limits.',
      triggered_rules: [],
      evidence_count: 1,
    },
    {
      gate_name: 'Error Handling',
      gate_number: 6,
      status: 'Warn',
      reason: 'Some error paths lack proper logging.',
      triggered_rules: ['RULE-6.1'],
      evidence_count: 1,
      fix_suggestion: 'Add structured logging to error paths.',
    },
    {
      gate_name: 'Data Privacy',
      gate_number: 7,
      status: 'Pass',
      reason: 'Data handling complies with privacy requirements.',
      triggered_rules: [],
      evidence_count: 1,
    },
    {
      gate_name: 'Operational Safety',
      gate_number: 8,
      status: 'Pass',
      reason: 'Operational safety checks passed.',
      triggered_rules: [],
      evidence_count: 0,
    },
  ],

  // Issues
  red_lines: [
    {
      issue_title: 'Execution boundary leakage detected',
      impact: 'CRITICAL',
      triggered_gate: 'Gate 4',
      rules: ['RULE-4.2', 'RULE-4.7'],
      why_blocking: 'The execution logic performs actions beyond the declared control scope, violating the Boundary Integrity gate.',
      required_disposition: 'Must tighten declared control boundaries, update ControlSpec, and resubmit.',
    },
    {
      issue_title: 'Undeclared action path detected',
      impact: 'HIGH',
      triggered_gate: 'Gate 4',
      rules: ['RULE-4.2'],
      why_blocking: 'An action path was discovered that was not declared in the control specification.',
      required_disposition: 'Must declare all action paths or remove the path, then resubmit.',
    },
  ],

  fixable_gaps: [
    {
      gap_title: 'Missing required annotation',
      severity: 'Medium',
      related_gate: 'Gate 2',
      suggested_fix: 'Add the missing @ControlScope annotation to the execute() method.',
      expected_outcome: 'Pass after re-audit of Gate 2.',
    },
    {
      gap_title: 'Error path lacks structured logging',
      severity: 'Low',
      related_gate: 'Gate 6',
      suggested_fix: 'Add structured logging to the exception handler in processPayment().',
      expected_outcome: 'Gate 6 warning will be cleared.',
    },
    {
      gap_title: 'Timeout value not configurable',
      severity: 'Medium',
      related_gate: 'Gate 5',
      suggested_fix: 'Make the timeout value configurable via environment variable.',
      expected_outcome: 'Improved flexibility for different deployment contexts.',
    },
    {
      gap_title: 'Documentation incomplete',
      severity: 'Low',
      related_gate: 'Gate 1',
      suggested_fix: 'Complete the missing documentation for private helper methods.',
      expected_outcome: 'Improved maintainability.',
    },
  ],

  // Governance Snapshot
  contract_control: {
    contract_summary: 'Asset governance contract: Skills assets must pass 8 Gate audit to ensure execution boundaries, control specifications, and evidence integrity meet requirements.',
    constitution_version: 'v2.1',
    rule_pack_version: 'v1.0.3',
    control_spec_version: 'v3.5',
    linked_manifest: 'manifest-2026-012',
    audit_scope: 'Full 8 Gate audit',
  },

  hash_binding: {
    demand_hash: 'sha256:abcd1234...',
    contract_hash: 'sha256:efgh5678...',
    decision_hash: 'sha256:a1b2c3d4...',
    revision_lineage: 'R-012 → R-013 → R-014',
    linked_manifest_id: 'manifest-2026-012',
  },
};

// Gather all evidence refs from gates
const allEvidenceRefs: EvidenceRef[] = [
  {
    id: 'EVD-001',
    source_type: 'File',
    summary: 'Control specification document',
    strength: 'Strong',
    visibility: 'visible',
    linked_gate: 'Gate 2',
  },
  {
    id: 'EVD-002',
    source_type: 'Log',
    summary: 'Execution trace showing boundary violation',
    strength: 'Strong',
    visibility: 'visible',
    linked_gate: 'Gate 4',
  },
  {
    id: 'EVD-003',
    source_type: 'Metric',
    summary: 'Resource usage metrics',
    strength: 'Medium',
    visibility: 'visible',
    linked_gate: 'Gate 5',
  },
  {
    id: 'EVD-004',
    source_type: 'Snapshot',
    summary: 'Gate boundary verification snapshot',
    strength: 'Strong',
    visibility: 'restricted',
    linked_gate: 'Gate 4',
  },
];

// ============================================
// Main Page Component
// ============================================

/**
 * AuditDetailPage - Main page component
 * @see T-FE-03 Section 3.2 Page Skeleton
 */
const AuditDetailPage: React.FC = () => {
  const { auditId } = useParams<{ auditId?: string }>();
  void auditId;
  const navigate = useNavigate();
  const { language } = useLanguage();
  const {
    draft,
    setDraft,
    draftIntentHint,
    setDraftIntentHint,
    latestTurn,
    latestTurns,
    activeDecision,
    submitDraft,
    isTyping,
  } = useGovernanceInteraction();
  useGovernancePromptQuerySync({ intentHint: 'audit' });

  // TODO: Replace with actual API call
  // const data = await fetchAuditDetail(auditId);
  const data = mockAuditData;

  // Gather evidence from all gates
  const evidenceRefs: EvidenceRef[] = allEvidenceRefs;
  const contextCopy =
    language === 'zh'
      ? {
          eyebrow: '当前输入上下文',
          title: '这张画布承接审计解释、缺口判断与裁决说明。',
          summary:
            '当输入被裁决为修订检查、证据审查、缺口分析或被阻止原因解释时，系统会把结果承接到这里，而不是让用户重新理解一个新页面。',
          promptLabel: '当前确认输入',
          statusLabel: '当前画布',
          statusValue: activeDecision.canvas === 'audit' ? 'Audit Detail' : 'Audit',
        }
      : {
          eyebrow: 'Current input context',
          title: 'This canvas carries audit explanation, gap review, and adjudication detail.',
          summary:
            'When the request resolves into revision review, evidence inspection, gap analysis, or blocked-decision explanation, the system carries the result here instead of forcing the user to re-learn a new page.',
          promptLabel: 'Confirmed input',
          statusLabel: 'Active canvas',
          statusValue: activeDecision.canvas === 'audit' ? 'Audit Detail' : 'Audit',
        };

  const quickActions: ComposerAction[] = [
    {
      label: language === 'zh' ? '导入外部 Skill' : 'Import external skill',
      prompt: language === 'zh' ? '审查这个外部 Skill 是否可以安装' : 'Vet whether this external skill can be installed',
      icon: '↘',
      intentHint: 'vetting',
    },
    {
      label: language === 'zh' ? '审查 Revision' : 'Review revision',
      prompt: language === 'zh' ? '解释为什么当前 Revision 被阻断' : 'Explain why the current revision is blocked',
      icon: '◎',
      intentHint: 'audit',
    },
    {
      label: language === 'zh' ? '申请 Permit' : 'Request permit',
      prompt: language === 'zh' ? '为这个 Skill 申请 Permit 放行' : 'Request permit release for this skill',
      icon: '◆',
      intentHint: 'permit',
    },
  ];

  const historyItems: ContextCanvasHistoryItem[] = latestTurns.map((turn) => ({
    id: turn.id,
    input: turn.userInput,
    state: turn.intent === 'unknown' ? contextCopy.statusValue : turn.intent,
  }));

  const slotConfig = useMemo(
    () => ({
      variant: 'context' as const,
      decision: activeDecision,
      confirmedValue: latestTurn?.userInput,
      showCanvas: Boolean(latestTurn && !isTyping),
      showHistory: Boolean(!isTyping && historyItems.length > 1),
      history: {
        title: contextCopy.promptLabel,
        subtitle: contextCopy.statusValue,
        items: historyItems,
      },
      consoleHeader: {
        eyebrow: contextCopy.eyebrow,
        title: contextCopy.title,
        meta: contextCopy.statusValue,
      },
      consoleHint: contextCopy.summary,
      composer: {
        value: draft,
        onChange: setDraft,
        onSubmit: async () => {
          await submitDraft({ intentHint: draftIntentHint });
        },
        placeholder:
          language === 'zh'
            ? '继续追问证据、缺口、阻断原因或下一步动作。'
            : 'Continue with evidence, gaps, blocked reasons, or next action questions.',
        submitLabel: language === 'zh' ? '确认输入' : 'Confirm Input',
        addAttachmentLabel: language === 'zh' ? '添加附件' : 'Add attachment',
        imageActionLabel: language === 'zh' ? '图片' : 'Image',
        fileActionLabel: language === 'zh' ? '文件' : 'File',
        enterKeyLabel: 'Enter',
        enterLabel: language === 'zh' ? '提交' : 'Submit',
        shiftEnterKeyLabel: 'Shift+Enter',
        newlineLabel: language === 'zh' ? '换行' : 'New line',
        separatorLabel: '·',
        imageAttachedLabel: language === 'zh' ? '已附加图片' : 'Image attached',
        fileAttachedLabel: language === 'zh' ? '已附加文件' : 'File attached',
        quickActions,
        onQuickActionSelect: (action: ComposerAction) => {
          setDraft(action.prompt);
          setDraftIntentHint(action.intentHint ?? 'unknown');
        },
        intentTabs: [
          { key: 'vetting' as const, label: language === 'zh' ? '导入外部 Skill' : 'Import External Skill' },
          { key: 'audit' as const, label: language === 'zh' ? '审查 Revision' : 'Review Revision' },
          { key: 'permit' as const, label: language === 'zh' ? '申请 Permit' : 'Request Permit' },
        ],
        selectedIntent: draftIntentHint,
        onIntentSelect: setDraftIntentHint,
      },
      onPrimaryAction: (decision: typeof activeDecision) => {
        if (decision.routeTarget && latestTurn?.userInput) {
          navigate(`${decision.routeTarget}?prompt=${encodeURIComponent(latestTurn.userInput)}`);
        }
      },
      onAlternativeSelect: (intent: 'vetting' | 'audit' | 'permit') => {
        if (!latestTurn?.userInput) return;
        navigate(`${INTENT_ROUTE_MAP[intent]}?prompt=${encodeURIComponent(latestTurn.userInput)}`);
      },
    }),
    [
      activeDecision,
      contextCopy.eyebrow,
      contextCopy.promptLabel,
      contextCopy.statusValue,
      contextCopy.summary,
      contextCopy.title,
      draft,
      draftIntentHint,
      historyItems,
      isTyping,
      language,
      latestTurn?.userInput,
      navigate,
      quickActions,
      setDraft,
      setDraftIntentHint,
      submitDraft,
    ],
  );

  useGovernanceCanvasSlot(slotConfig);

  return (
    <main className={styles['audit-detail-page']}>
      {/* [1] Decision Header */}
      <DecisionHeader data={data} />

      {/* [2] Decision Summary + [3] Power Boundary */}
      <div className={styles['summary-boundary-row']}>
        <DecisionSummaryCard data={data} />
        <PowerBoundaryCard />
      </div>

      {/* Main Content: [4] 8 Gate + [5] EvidenceRef */}
      <div className={styles['main-content-row']}>
        <GateTimelineCard gates={data.gate_results} />
        <EvidenceRefPanel evidenceRefs={evidenceRefs} />
      </div>

      {/* [6] Issue Breakdown: Red Lines + Fixable Gaps */}
      <IssueBreakdownRow
        redLines={data.red_lines}
        fixableGaps={data.fixable_gaps}
      />

      {/* [7] Governance Snapshot: Contract/Control + Hash/Reproducibility */}
      <GovernanceSnapshotRow
        contractControl={data.contract_control}
        hashBinding={data.hash_binding}
      />

      {/* [8] Footer Action Bar */}
      <FooterActionBar status={data.current_status} />
    </main>
  );
};

export default AuditDetailPage;
