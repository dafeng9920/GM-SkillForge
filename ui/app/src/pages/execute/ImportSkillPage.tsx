/**
 * Import Skill Page - 六步流水线可视化 + Fail-Closed 断点恢复交互
 *
 * 功能描述：
 * - 外部技能导入向导（6步治理流水线可视化）
 * - 支持断点恢复（每步 FAIL 时展示 evidence_ref）
 * - 提供重试本步/放弃并回滚 两个动作位
 * - required_changes 列表可展开查看
 *
 * 六步流水线：
 * - S1: QUARANTINE (导入到隔离区)
 * - S2: CONSTITUTION_GATE (宪章门控检查)
 * - S3: SYSTEM_AUDIT (L1-L5 系统审计)
 * - S4: DECISION (决策)
 * - S5: PERMIT_ISSUANCE (许可证签发)
 * - S6: REGISTRY_ADMISSION (注册表接纳)
 *
 * @module pages/execute/ImportSkillPage
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md
 */

import React, { useState, useCallback } from 'react';
import { PipelineStepPanel, PipelineStep, AuditLayer } from '../../components/governance/PipelineStepPanel';
import styles from './ImportSkillPage.module.css';

// ============================================
// Types
// ============================================

export type PipelineStepStatus = 'PENDING' | 'IN_PROGRESS' | 'PASS' | 'FAIL';

export interface ImportSkillFormData {
  repo_url: string;
  commit_sha: string;
  external_skill_ref: string;
  requester_id: string;
  skill_name?: string;
  skill_version?: string;
  source_repository?: string;
  tier: string;
}

export interface ImportSkillResult {
  quarantine_id?: string;
  permit_id?: string;
  registry_entry_id?: string;
  skill_revision?: number;
  audit_summary?: Record<string, { status: string; score: number }>;
  import_status: string;
  pipeline_state: string;
}

export interface ImportSkillResponse {
  ok: boolean;
  run_id: string;
  evidence_ref: string;
  gate_decision: 'ALLOW' | 'BLOCK';
  release_allowed: boolean;
  data?: ImportSkillResult;
  error_code?: string;
  blocked_by?: string;
  message?: string;
  required_changes?: string[];
}

// ============================================
// Constants
// ============================================

const PIPELINE_STEPS: { id: string; name: string; description: string }[] = [
  { id: 'S1_QUARANTINE', name: 'S1 隔离', description: '导入到隔离区' },
  { id: 'S2_CONSTITUTION_GATE', name: 'S2 宪章', description: '宪章门控检查（边界/权限/禁止能力）' },
  { id: 'S3_SYSTEM_AUDIT', name: 'S3 审计', description: 'L1-L5 系统审计' },
  { id: 'S4_DECISION', name: 'S4 决策', description: '决策（需要 PASS@L3+）' },
  { id: 'S5_PERMIT_ISSUANCE', name: 'S5 许可', description: '许可证签发' },
  { id: 'S6_REGISTRY_ADMISSION', name: 'S6 注册', description: '注册表接纳' },
];

const DEFAULT_AUDIT_LAYERS: AuditLayer[] = [
  { id: 'L1', name: 'contract_audit', label: 'L1 合约审计', status: 'PENDING', score: 0 },
  { id: 'L2', name: 'control_audit', label: 'L2 控制审计', status: 'PENDING', score: 0 },
  { id: 'L3', name: 'security_audit', label: 'L3 安全审计', status: 'PENDING', score: 0 },
  { id: 'L4', name: 'evidence_audit', label: 'L4 证据审计', status: 'PENDING', score: 0 },
  { id: 'L5', name: 'reproducibility_audit', label: 'L5 可复现性审计', status: 'PENDING', score: 0 },
];

const API_BASE_URL = 'http://localhost:8000/api/v1';

// ============================================
// Mock Data Generator (for demo/testing)
// ============================================

function generateMockResponse(success: boolean): ImportSkillResponse {
  const runId = `RUN-N8N-${Date.now()}-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
  const evidenceRef = `EV-EXT-SKILL-${Date.now()}-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;

  if (success) {
    return {
      ok: true,
      run_id: runId,
      evidence_ref: evidenceRef,
      gate_decision: 'ALLOW',
      release_allowed: true,
      data: {
        quarantine_id: `Q-${Math.random().toString(36).substring(2, 14).toUpperCase()}`,
        permit_id: `PERMIT-EXT-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
        registry_entry_id: `REG-${Math.random().toString(36).substring(2, 14).toUpperCase()}`,
        skill_revision: 1,
        audit_summary: {
          L1_contract_audit: { status: 'PASS', score: 95 },
          L2_control_audit: { status: 'PASS', score: 90 },
          L3_security_audit: { status: 'PASS', score: 88 },
          L4_evidence_audit: { status: 'PASS', score: 92 },
          L5_reproducibility_audit: { status: 'PASS', score: 85 },
        },
        import_status: 'COMPLETED',
        pipeline_state: 'S6_REGISTRY_ADMISSION',
      },
    };
  } else {
    return {
      ok: false,
      run_id: runId,
      evidence_ref: evidenceRef,
      gate_decision: 'BLOCK',
      release_allowed: false,
      error_code: 'SYSTEM_AUDIT_FAILED',
      blocked_by: 'AUDIT_FAILURE',
      message: 'System audit failed: 3/5 layers passed',
      required_changes: [
        'Fix L3_security_audit: score too low (current: 45, required: 60)',
        'Fix L5_reproducibility_audit: score too low (current: 50, required: 60)',
        'Need at least 4/5 layers to pass, got 3',
      ],
    };
  }
}

// ============================================
// Sub-Components
// ============================================

const FormInput: React.FC<{
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  type?: 'text' | 'select';
  options?: { value: string; label: string }[];
  disabled?: boolean;
}> = ({ label, value, onChange, placeholder, required, type = 'text', options, disabled }) => (
  <div className={styles['form-field']}>
    <label className={styles['form-label']}>
      {label}
      {required && <span className={styles.required}>*</span>}
    </label>
    {type === 'select' ? (
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={styles['form-select']}
      >
        {options?.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    ) : (
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={styles['form-input']}
      />
    )}
  </div>
);

const CopyableText: React.FC<{ text: string; label?: string }> = ({ text, label }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [text]);

  return (
    <div className={styles['copy-container']}>
      {label && <span className={styles['copy-label']}>{label}: </span>}
      <code className={styles['copy-code']}>{text}</code>
      <button onClick={handleCopy} className={styles['copy-btn-small']}>
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
};

const RequiredChangesList: React.FC<{ changes: string[] }> = ({ changes }) => {
  const [expanded, setExpanded] = useState(true);

  if (!changes || changes.length === 0) return null;

  return (
    <div className={styles['required-changes-container']}>
      <button
        className={styles['required-changes-header']}
        onClick={() => setExpanded(!expanded)}
      >
        <span>
          Required Changes ({changes.length})
        </span>
        <span className={styles['expand-icon']}>{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <ul className={`${styles['result-details']} ${styles['bg-transparent']} ${styles['m-0']}`}>
          {changes.map((change, index) => (
            <li key={index} className={`${styles['result-field']} ${styles['justify-start']} ${styles['text-primary']}`}>
              <span className={`${styles['result-label']} ${styles['mr-2']}`}>{index + 1}.</span>
              <span>{change}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const ResultCard: React.FC<{
  result: ImportSkillResult;
  runId: string;
  evidenceRef: string;
}> = ({ result, runId, evidenceRef }) => (
  <div className={styles.card}>
    <header className={styles['error-header']}>
      <h3 className={`${styles['card-title']} ${styles['margin-0']}`}>Import Completed</h3>
      <span className={`${styles['status-badge']} ${styles['status-badge-success']}`}>SUCCESS</span>
    </header>
    <div>
      <CopyableText text={runId} label="run_id" />
      <CopyableText text={evidenceRef} label="evidence_ref" />
      <div className={styles['result-details']}>
        <div className={styles['result-field']}>
          <span className={styles['result-label']}>quarantine_id:</span>
          <code className={styles['result-value']}>{result.quarantine_id}</code>
        </div>
        <div className={styles['result-field']}>
          <span className={styles['result-label']}>permit_id:</span>
          <code className={styles['result-value']}>{result.permit_id}</code>
        </div>
        <div className={styles['result-field']}>
          <span className={styles['result-label']}>registry_entry_id:</span>
          <code className={styles['result-value']}>{result.registry_entry_id}</code>
        </div>
        <div className={styles['result-field']}>
          <span className={styles['result-label']}>skill_revision:</span>
          <code className={styles['result-value']}>{result.skill_revision}</code>
        </div>
      </div>
    </div>
  </div>
);

// ============================================
// Main Component
// ============================================

export const ImportSkillPage: React.FC = () => {
  // Form state
  const [formData, setFormData] = useState<ImportSkillFormData>({
    repo_url: '',
    commit_sha: '',
    external_skill_ref: '',
    requester_id: '',
    skill_name: '',
    skill_version: '',
    source_repository: '',
    tier: 'FREE',
  });

  // Pipeline state
  const [steps, setSteps] = useState<PipelineStep[]>(
    PIPELINE_STEPS.map((step) => ({
      id: step.id,
      name: step.name,
      description: step.description,
      status: 'PENDING' as PipelineStepStatus,
    }))
  );

  const [auditLayers, setAuditLayers] = useState<AuditLayer[]>(DEFAULT_AUDIT_LAYERS);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(-1);
  const [isRunning, setIsRunning] = useState(false);
  const [response, setResponse] = useState<ImportSkillResponse | null>(null);
  const [useMock, setUseMock] = useState(true); // Toggle for demo mode

  // Update form field
  const updateFormField = useCallback((field: keyof ImportSkillFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  // Simulate step progression
  const simulatePipeline = useCallback(async (success: boolean) => {
    setIsRunning(true);
    setResponse(null);

    // Reset steps
    const resetSteps = PIPELINE_STEPS.map((step) => ({
      id: step.id,
      name: step.name,
      description: step.description,
      status: 'PENDING' as PipelineStepStatus,
    }));
    setSteps(resetSteps);
    setAuditLayers(DEFAULT_AUDIT_LAYERS);

    const failAtStep = success ? 6 : 3; // S3 if fail, S6 if success

    for (let i = 0; i < failAtStep; i++) {
      // Set current step to IN_PROGRESS
      setCurrentStepIndex(i);
      setSteps((prev) =>
        prev.map((step, idx) =>
          idx === i ? { ...step, status: 'IN_PROGRESS' } : step
        )
      );

      // Simulate delay
      await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 400));

      // Update audit layers for S3
      if (i === 2) {
        const auditResults = success
          ? [
            { status: 'PASS' as const, score: 95 },
            { status: 'PASS' as const, score: 90 },
            { status: 'PASS' as const, score: 88 },
            { status: 'PASS' as const, score: 92 },
            { status: 'PASS' as const, score: 85 },
          ]
          : [
            { status: 'PASS' as const, score: 95 },
            { status: 'PASS' as const, score: 90 },
            { status: 'FAIL' as const, score: 45 },
            { status: 'PASS' as const, score: 92 },
            { status: 'FAIL' as const, score: 50 },
          ];

        setAuditLayers(
          DEFAULT_AUDIT_LAYERS.map((layer, idx) => ({
            ...layer,
            status: auditResults[idx].status,
            score: auditResults[idx].score,
          }))
        );
      }

      // Set step to PASS
      setSteps((prev) =>
        prev.map((step, idx) =>
          idx === i ? { ...step, status: 'PASS' } : step
        )
      );
    }

    // Handle failure case
    if (!success) {
      setSteps((prev) =>
        prev.map((step, idx) =>
          idx === failAtStep ? { ...step, status: 'FAIL' } : step
        )
      );
    }

    // Generate response
    const mockResponse = generateMockResponse(success);
    setResponse(mockResponse);
    setCurrentStepIndex(-1);
    setIsRunning(false);
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (useMock) {
      // Demo mode: simulate with success randomly
      simulatePipeline(Math.random() > 0.3);
      return;
    }

    // Real API call
    setIsRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/n8n/import_external_skill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data: ImportSkillResponse = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Import failed:', error);
      setResponse({
        ok: false,
        run_id: `RUN-ERROR-${Date.now()}`,
        evidence_ref: `EV-ERROR-${Date.now()}`,
        gate_decision: 'BLOCK',
        release_allowed: false,
        error_code: 'NETWORK_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsRunning(false);
    }
  }, [formData, useMock, simulatePipeline]);

  // Handle retry
  const handleRetry = useCallback(() => {
    simulatePipeline(true);
  }, [simulatePipeline]);

  // Handle rollback
  const handleRollback = useCallback(() => {
    setSteps(
      PIPELINE_STEPS.map((step) => ({
        id: step.id,
        name: step.name,
        description: step.description,
        status: 'PENDING' as PipelineStepStatus,
      }))
    );
    setAuditLayers(DEFAULT_AUDIT_LAYERS);
    setResponse(null);
  }, []);

  // Form validation
  const isFormValid =
    formData.repo_url.trim() !== '' &&
    formData.commit_sha.trim() !== '' &&
    formData.external_skill_ref.trim() !== '' &&
    formData.requester_id.trim() !== '';

  return (
    <div className={styles.page}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles['header-left']}>
          <h1 className={styles.title}>Import External Skill</h1>
          <span className={styles.subtitle}>6-Stage Governance Pipeline</span>
        </div>
        <div className={styles['header-right']}>
          <label className={styles['demo-toggle']}>
            <input
              type="checkbox"
              checked={useMock}
              onChange={(e) => setUseMock(e.target.checked)}
            />
            <span>Demonstration Mode</span>
          </label>
        </div>
      </header>

      <main className={styles.main}>
        {/* Left Panel: Form */}
        <div className={styles['left-panel']}>
          <div className={styles.card}>
            <h2 className={styles['card-title']}>Execution Parameters</h2>
            <form onSubmit={handleSubmit}>
              <FormInput
                label="Repository URL"
                value={formData.repo_url}
                onChange={(v) => updateFormField('repo_url', v)}
                placeholder="https://github.com/org/repo"
                required
                disabled={isRunning}
              />
              <FormInput
                label="Commit SHA"
                value={formData.commit_sha}
                onChange={(v) => updateFormField('commit_sha', v)}
                placeholder="40-char Hash"
                required
                disabled={isRunning}
              />
              <FormInput
                label="External Skill Ref"
                value={formData.external_skill_ref}
                onChange={(v) => updateFormField('external_skill_ref', v)}
                placeholder="Package Reference"
                required
                disabled={isRunning}
              />
              <FormInput
                label="Requester ID"
                value={formData.requester_id}
                onChange={(v) => updateFormField('requester_id', v)}
                placeholder="Identity string"
                required
                disabled={isRunning}
              />
              <FormInput
                label="Skill Name"
                value={formData.skill_name || ''}
                onChange={(v) => updateFormField('skill_name', v)}
                placeholder="Optional"
                disabled={isRunning}
              />
              <FormInput
                label="Skill Version"
                value={formData.skill_version || ''}
                onChange={(v) => updateFormField('skill_version', v)}
                placeholder="Optional"
                disabled={isRunning}
              />
              <FormInput
                label="Membership Tier"
                value={formData.tier}
                onChange={(v) => updateFormField('tier', v)}
                type="select"
                options={[
                  { value: 'FREE', label: 'FREE' },
                  { value: 'PRO', label: 'PRO' },
                  { value: 'ENTERPRISE', label: 'ENTERPRISE' },
                ]}
                disabled={isRunning}
              />
              <div className={styles['form-actions']}>
                <button
                  type="submit"
                  disabled={!isFormValid || isRunning}
                  className={`${styles['submit-btn']} ${(!isFormValid || isRunning) ? styles['submit-btn-disabled'] : ''}`}
                >
                  {isRunning ? 'Processing...' : 'Start Execution'}
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({
                    repo_url: '',
                    commit_sha: '',
                    external_skill_ref: '',
                    requester_id: '',
                    skill_name: '',
                    skill_version: '',
                    source_repository: '',
                    tier: 'FREE',
                  })}
                  disabled={isRunning}
                  className={styles['reset-btn']}
                >
                  Clear Form
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Panel: Pipeline */}
        <div className={styles['right-panel']}>
          {/* Pipeline Steps */}
          <div className={styles.card}>
            <h2 className={styles['card-title']}>Execution Pipeline</h2>
            <PipelineStepPanel
              steps={steps}
              currentStepIndex={currentStepIndex}
              auditLayers={auditLayers}
              onRetry={handleRetry}
              onRollback={handleRollback}
              isRunning={isRunning}
            />
          </div>

          {/* Response / Result */}
          {response && (
            <div className={styles.card}>
              {response.ok ? (
                <>
                  {response.data && (
                    <ResultCard
                      result={response.data}
                      runId={response.run_id}
                      evidenceRef={response.evidence_ref}
                    />
                  )}
                </>
              ) : (
                <>
                  <header className={styles['error-header']}>
                    <h2 className={`${styles['card-title']} ${styles['margin-0']}`}>Execution Blocked</h2>
                    <span className={`${styles['status-badge']} ${styles['status-badge-error']}`}>
                      {response.error_code}
                    </span>
                  </header>
                  <CopyableText text={response.run_id} label="run_id" />
                  <CopyableText text={response.evidence_ref} label="evidence_ref" />
                  <div className={styles['error-msg']}>
                    <strong>Blocked By:</strong> {response.blocked_by}
                  </div>
                  <div className={styles['error-msg']}>
                    <strong>Details:</strong> {response.message}
                  </div>
                  {response.required_changes && (
                    <RequiredChangesList changes={response.required_changes} />
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default ImportSkillPage;
