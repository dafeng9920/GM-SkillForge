/**
 * DecisionHeroCard - Gate Decision Hero Display Component
 *
 * Displays gate_decision and release_allowed as the first visual element.
 * Follows the "conclusion first, details later" principle.
 *
 * @module components/governance/DecisionHeroCard
 */

import React, { useState, useCallback } from 'react';
import type { GateDecision } from '../../types/orchestrationProjection';
import styles from './DecisionHeroCard.module.css';

export interface DecisionHeroCardProps {
  /** Gate decision: ALLOW, BLOCK, DENY, REQUIRES_CHANGES */
  gateDecision: GateDecision;
  /** Whether release is allowed */
  releaseAllowed: boolean;
  /** Evidence reference */
  evidenceRef?: string;
  /** Run ID */
  runId: string;
  /** Permit ID if available */
  permitId?: string | null;
  /** Validation timestamp */
  validationTimestamp?: string | null;
  /** Optional: callback when evidence is clicked */
  onClickEvidence?: () => void;
  /** Optional: callback when copy is triggered */
  onCopy?: (text: string) => void;
}

export const DecisionHeroCard: React.FC<DecisionHeroCardProps> = ({
  gateDecision,
  releaseAllowed,
  evidenceRef,
  runId,
  permitId,
  validationTimestamp,
  onClickEvidence,
  onCopy,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopy?.(text);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [onCopy]);

  const copyCombinedRef = useCallback(() => {
    if (runId && evidenceRef) {
      handleCopy(`${runId}:${evidenceRef}`);
    }
  }, [runId, evidenceRef, handleCopy]);

  const isAllowed = gateDecision === 'ALLOW' && releaseAllowed;
  const isBlocked = gateDecision === 'BLOCK' || gateDecision === 'DENY';
  const requiresChanges = gateDecision === 'REQUIRES_CHANGES';

  const getStatusClass = () => {
    if (isAllowed) return styles['status-allowed'];
    if (isBlocked) return styles['status-blocked'];
    if (requiresChanges) return styles['status-warning'];
    return styles['status-pending'];
  };

  const getStatusIcon = () => {
    if (isAllowed) return '✓';
    if (isBlocked) return '✕';
    if (requiresChanges) return '⚠';
    return '⏳';
  };

  const getStatusText = () => {
    if (isAllowed) return 'ALLOWED';
    if (isBlocked) return 'BLOCKED';
    if (requiresChanges) return 'REQUIRES CHANGES';
    return 'PENDING';
  };

  const formatTimestamp = (ts: string | null | undefined) => {
    if (!ts) return 'N/A';
    try {
      return new Date(ts).toLocaleString();
    } catch {
      return ts;
    }
  };

  return (
    <article className={`${styles.card} ${getStatusClass()}`} aria-live="polite">
      {/* Main status display - first visual element */}
      <header className={styles['hero-header']}>
        <div className={styles['icon-container']} aria-hidden="true">
          {getStatusIcon()}
        </div>
        <div className={styles['hero-title-container']}>
          <h2 className={styles['hero-title']}>{getStatusText()}</h2>
          <div className={styles['hero-subtitle']}>
            {isAllowed ? 'Execution permitted by governance gate' : 'Execution intercepted and blocked'}
          </div>
        </div>
      </header>

      {/* Key metrics row */}
      <div className={styles['metrics-grid']}>
        {/* Gate Decision */}
        <div className={styles['metric-item']}>
          <span className={styles['metric-label']}>Gate Decision</span>
          <span className={`${styles['metric-value']} ${styles[`badge-${gateDecision.toLowerCase()}`]}`}>
            {gateDecision}
          </span>
        </div>

        {/* Release Allowed */}
        <div className={styles['metric-item']}>
          <span className={styles['metric-label']}>Release Control</span>
          <span className={`${styles['metric-value']} ${releaseAllowed ? styles['metric-pass'] : styles['metric-block']}`}>
            {releaseAllowed ? '✓ Allowed' : '✕ Blocked'}
          </span>
        </div>

        {/* Permit ID */}
        <div className={styles['metric-item']}>
          <span className={styles['metric-label']}>Execution Permit</span>
          <span className={`${styles['metric-value']} ${styles['metric-value-mono']}`}>
            {permitId || 'N/A'}
          </span>
        </div>
      </div>

      {/* Evidence section - clickable and copyable */}
      <footer className={styles['evidence-footer']}>
        <div className={styles['evidence-row']}>
          <span className={`${styles['metric-label']} ${styles['min-w-100']}`}>Evidence</span>
          {evidenceRef ? (
            <div className={styles['evidence-actions']}>
              <button
                className={styles['mono-link']}
                onClick={onClickEvidence}
                title="View evidence details"
              >
                {evidenceRef}
              </button>
              <button
                className={styles['copy-btn']}
                onClick={copyCombinedRef}
                title="Copy run_id:evidence_ref"
              >
                {copied ? '✓ Copied' : '📋 Extract Reference'}
              </button>
            </div>
          ) : (
            <span className={`${styles['metric-value-mono']} ${styles['text-muted']}`}>N/A</span>
          )}
        </div>

        <div className={styles['evidence-row']}>
          <span className={`${styles['metric-label']} ${styles['min-w-100']}`}>Run ID</span>
          <div className={styles['evidence-actions']}>
            <span className={styles['metric-value-mono']}>{runId}</span>
            <button
              className={styles['copy-btn']}
              onClick={() => handleCopy(runId)}
              title="Copy run_id"
              aria-label="Copy run id to clipboard"
            >
              📋
            </button>
          </div>
        </div>

        {validationTimestamp && (
          <div className={styles['evidence-row']}>
            <span className={`${styles['metric-label']} ${styles['min-w-100']}`}>Validated At</span>
            <span className={`${styles['metric-value-mono']} ${styles['text-secondary']}`}>
              {formatTimestamp(validationTimestamp)}
            </span>
          </div>
        )}
      </footer>
    </article>
  );
};

export default DecisionHeroCard;
