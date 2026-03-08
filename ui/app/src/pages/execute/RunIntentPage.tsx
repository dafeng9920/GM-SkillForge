/**
 * Run Intent Page
 *
 * 执行意图页面 - P0 优先级
 *
 * 功能：执行 n8n 意图并展示结果
 * API: POST /api/v1/n8n/run_intent
 *
 * 设计规范：
 * - 先结论后细节：首屏展示 gate_decision + release_allowed
 * - run_id / evidence_ref 可复制
 * - 统一卡片结构
 */

import React, { useState } from 'react';
import { DecisionHeroCard } from '../../components/governance/DecisionHeroCard';
import { BlockReasonCard } from '../../components/governance/BlockReasonCard';
import { DualChannelWorkbench } from '../../components/governance/DualChannelWorkbench';
import type { GateDecision } from '../../types/orchestrationProjection';
import styles from './RunIntentPage.module.css';

// 类型定义
interface RunIntentForm {
  repo_url: string;
  commit_sha: string;
  at_time: string;
  intent_id: string;
  requester_id: string;
  tier: 'FREE' | 'PRO' | 'ENTERPRISE';
  context?: Record<string, unknown>;
}

interface RunIntentResult {
  run_id: string;
  gate_decision: 'ALLOW' | 'BLOCK';
  release_allowed: boolean;
  evidence_ref: string;
  permit_id?: string;
  execution_status?: string;
}

export const RunIntentPage: React.FC = () => {
  const [form, setForm] = useState<RunIntentForm>({
    repo_url: '',
    commit_sha: '',
    at_time: '',
    intent_id: '',
    requester_id: '',
    tier: 'FREE',
  });

  const [result, setResult] = useState<RunIntentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // TODO: 实际 API 调用
      // const response = await fetch('/api/v1/n8n/run_intent', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(form),
      // });

      // 模拟响应
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setResult({
        run_id: `RUN-N8N-${Date.now()}`,
        gate_decision: 'ALLOW',
        release_allowed: true,
        evidence_ref: `EV-${Date.now()}`,
        permit_id: `PERMIT-${Date.now()}`,
        execution_status: 'COMPLETED',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '执行失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setForm({
      repo_url: '',
      commit_sha: '',
      at_time: '',
      intent_id: '',
      requester_id: '',
      tier: 'FREE',
    });
    setResult(null);
    setError(null);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Build the Header Governance Logic
  const renderGovernanceHeader = () => {
    if (!result) {
      return (
        <div style={{ padding: 'var(--gm-space-4)', display: 'flex', alignItems: 'center', gap: 'var(--gm-space-4)' }}>
          <span className={styles.title} style={{ margin: 0 }}>执行意图 // STANDBY</span>
        </div>
      );
    }

    if (result.gate_decision === 'ALLOW') {
      return (
        <DecisionHeroCard
          gateDecision={result.gate_decision as GateDecision}
          releaseAllowed={result.release_allowed}
          evidenceRef={result.evidence_ref}
          runId={result.run_id}
          permitId={result.permit_id}
          onCopy={copyToClipboard}
        />
      );
    }

    return (
      <BlockReasonCard
        errorCode="GATE_BLOCKED"
        blockedBy="GateCheck"
        message="Request was blocked by gate decision"
        evidenceRef={result.evidence_ref}
        runId={result.run_id}
      />
    );
  };

  // Build the Channel A (Cognition) slot
  const renderCognitionSlot = () => (
    <div className={styles['cognition-card']}>
      <h3 className={styles['cognition-header']}>Analysis Context</h3>
      {!result ? (
        <div className={styles['empty-state']}>
          Wait for intent execution to generate cognitive reasoning...
        </div>
      ) : (
        <div className={styles['cognition-text']}>
          [INTENT ASSESSED]: High Confidence
          <br /><br />
          The requested git commit deployment satisfies all current execution contracts. No forbidden fields mutated.
          <br /><br />
          <strong style={{ color: 'var(--gm-color-state-pass)' }}>Risk Profile: LOW</strong>
        </div>
      )}
    </div>
  );

  // Build the Channel B (Execution) slot
  const renderExecutionSlot = () => (
    <>
      <div className={styles.card}>
        <h2 className={styles.title}>
          <span>📝</span>
          执行参数
        </h2>

        {/* 表单区 */}
        <form onSubmit={handleSubmit}>
          <div className={styles['form-row']}>
            <label className={styles.label}>
              repo_url <span className={styles['required-asterisk']}>*</span>
            </label>
            <input
              type="url"
              name="repo_url"
              value={form.repo_url}
              onChange={handleInputChange}
              placeholder="https://github.com/org/repo"
              required
              className={styles.input}
            />
          </div>

          <div className={styles['form-row']}>
            <label className={styles.label}>
              commit_sha <span className={styles['required-asterisk']}>*</span>
            </label>
            <input
              type="text"
              name="commit_sha"
              value={form.commit_sha}
              onChange={handleInputChange}
              placeholder="40位 Git 提交哈希"
              required
              maxLength={40}
              className={styles.input}
            />
          </div>

          <div className={styles['form-row']}>
            <label className={styles.label}>at_time</label>
            <input
              type="datetime-local"
              name="at_time"
              value={form.at_time}
              onChange={handleInputChange}
              className={styles.input}
            />
          </div>

          <div className={styles['form-row']}>
            <label className={styles.label}>
              intent_id <span className={styles['required-asterisk']}>*</span>
            </label>
            <input
              type="text"
              name="intent_id"
              value={form.intent_id}
              onChange={handleInputChange}
              placeholder="意图标识"
              required
              className={styles.input}
            />
          </div>

          <div className={styles['form-row']}>
            <label className={styles.label}>
              requester_id <span className={styles['required-asterisk']}>*</span>
            </label>
            <input
              type="text"
              name="requester_id"
              value={form.requester_id}
              onChange={handleInputChange}
              placeholder="请求者标识"
              required
              className={styles.input}
            />
          </div>

          <div className={styles['form-row']}>
            <label className={styles.label}>tier</label>
            <select
              name="tier"
              value={form.tier}
              onChange={handleInputChange}
              className={`${styles.input} ${styles['input-select']}`}
            >
              <option value="FREE">FREE</option>
              <option value="PRO">PRO</option>
              <option value="ENTERPRISE">ENTERPRISE</option>
            </select>
          </div>

          <div className={styles['button-group']}>
            <button
              type="submit"
              disabled={loading}
              className={`${styles.btn} ${styles['btn-primary']} ${loading ? styles['is-loading'] : ''}`}
            >
              {loading ? '执行中...' : '执行'}
            </button>
            <button type="button" onClick={handleReset} className={`${styles.btn} ${styles['btn-secondary']}`}>
              重置
            </button>
          </div>
        </form>
      </div>

      {/* 错误区 */}
      {error && (
        <div className={`${styles.card} ${styles['error-card']}`}>
          <h3 className={`${styles.title} ${styles['error-title']}`}>
            ⚠️ 执行失败
          </h3>
          <p className={styles['error-text']}>{error}</p>
        </div>
      )}
    </>
  );

  return (
    <DualChannelWorkbench
      headerSlot={renderGovernanceHeader()}
      cognitionSlot={renderCognitionSlot()}
      executionSlot={renderExecutionSlot()}
    />
  );
};


export default RunIntentPage;
