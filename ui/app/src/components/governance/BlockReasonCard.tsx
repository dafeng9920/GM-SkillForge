/**
 * BlockReasonCard - Global Unified Error Interception Component
 *
 * Implements the unified BLOCK scenario display with:
 * - Interception conclusion (gate_decision / blocked_by)
 * - Triggered rules (error_code / required_changes)
 * - Evidence references (evidence_ref / run_id)
 * - Suggested fixes (required_changes / next_action)
 *
 * Constraint: ALL BLOCK scenarios MUST use this component.
 * NO scattered custom error styles across pages.
 *
 * @module components/governance/BlockReasonCard
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md Section 6 (Error Codes)
 */

import React, { useState, useCallback } from 'react';
import styles from './BlockReasonCard.module.css';

// ============================================
// Type Definitions
// ============================================

/** Gate decision types */
export type GateDecision = 'ALLOW' | 'BLOCK' | 'DENY' | 'REQUIRES_CHANGES';

/** N8N Error envelope structure */
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

/** Permit error codes */
export type PermitErrorCode = 'E001' | 'E002' | 'E003' | 'E004' | 'E005' | 'E006' | 'E007';

/** N8N error codes */
export type N8nErrorCode =
  | 'N8N_FORBIDDEN_FIELD_INJECTION'
  | 'N8N_PERMIT_ISSUE_FAILED'
  | 'N8N_MEMBERSHIP_DENIED'
  | 'N8N_MISSING_IDENTIFIER'
  | 'N8N_INTERNAL_ERROR'
  | 'RAG-AT-TIME-MISSING'
  | 'RAG-AT-TIME-DRIFT-FORBIDDEN'
  | 'RAG-VALIDATION-ERROR'
  | 'RAG-INTERNAL-ERROR'
  | 'CONSTITUTION_GATE_FAILED'
  | 'SYSTEM_AUDIT_FAILED'
  | 'IMPORT_INTERNAL_ERROR';

/** Union of all possible error codes */
export type BlockErrorCode = PermitErrorCode | N8nErrorCode | string;

/** Props for BlockReasonCard */
export interface BlockReasonCardProps {
  /** The error code that caused the block */
  errorCode: BlockErrorCode;

  /** Human-readable blocked-by description */
  blockedBy: string;

  /** Detailed error message */
  message: string;

  /** Evidence reference for audit trail */
  evidenceRef?: string;

  /** Run ID for tracking */
  runId: string;

  /** List of required changes to unblock */
  requiredChanges?: string[];

  /** Suggested next action for the user */
  suggestedAction?: string;

  /** Optional: Forbidden field evidence (for security warnings) */
  forbiddenFieldEvidence?: Record<string, unknown> | null;

  /** Optional: Additional context data */
  context?: Record<string, unknown>;

  /** Optional: Custom title override */
  title?: string;

  /** Optional: Callback when evidence is clicked */
  onEvidenceClick?: (evidenceRef: string) => void;

  /** Optional: Callback when run_id is clicked */
  onRunIdClick?: (runId: string) => void;

  /** Optional: Show compact mode */
  compact?: boolean;
}

// ============================================
// Error Code Registry (Documented)
// ============================================

/**
 * Error code metadata for user-friendly display
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md Section 6
 */
export const ERROR_CODE_REGISTRY: Record<string, {
  severity: 'critical' | 'error' | 'warning';
  category: 'security' | 'governance' | 'validation' | 'system';
  shortDesc: string;
  suggestedAction: string;
}> = {
  // Permit Errors (E001-E007)
  E001: {
    severity: 'critical',
    category: 'governance',
    shortDesc: 'No Permit',
    suggestedAction: 'Request a valid permit from the governance system.',
  },
  E002: {
    severity: 'critical',
    category: 'governance',
    shortDesc: 'Invalid Permit',
    suggestedAction: 'Re-issue the permit through the permit gate.',
  },
  E003: {
    severity: 'critical',
    category: 'security',
    shortDesc: 'Signature Verification Failed',
    suggestedAction: 'Security alert! Contact system administrator.',
  },
  E004: {
    severity: 'warning',
    category: 'governance',
    shortDesc: 'Permit Expired',
    suggestedAction: 'Renew the permit to extend validity.',
  },
  E005: {
    severity: 'error',
    category: 'governance',
    shortDesc: 'Scope Mismatch',
    suggestedAction: 'Check the request scope against permit allowed_actions.',
  },
  E006: {
    severity: 'error',
    category: 'governance',
    shortDesc: 'Subject Mismatch',
    suggestedAction: 'Verify identity authentication.',
  },
  E007: {
    severity: 'critical',
    category: 'governance',
    shortDesc: 'Permit Revoked',
    suggestedAction: 'Contact administrator for permit status.',
  },

  // N8N Errors
  N8N_FORBIDDEN_FIELD_INJECTION: {
    severity: 'critical',
    category: 'security',
    shortDesc: 'Forbidden Field Injection',
    suggestedAction: 'Security violation detected. Contact admin immediately.',
  },
  N8N_PERMIT_ISSUE_FAILED: {
    severity: 'error',
    category: 'system',
    shortDesc: 'Permit Issuance Failed',
    suggestedAction: 'Check service configuration (e.g., PERMIT_HS256_KEY).',
  },
  N8N_MEMBERSHIP_DENIED: {
    severity: 'warning',
    category: 'governance',
    shortDesc: 'Membership Denied',
    suggestedAction: 'Upgrade membership tier for this operation.',
  },
  N8N_MISSING_IDENTIFIER: {
    severity: 'error',
    category: 'validation',
    shortDesc: 'Missing Identifier',
    suggestedAction: 'Provide at least one of: run_id or evidence_ref.',
  },
  N8N_INTERNAL_ERROR: {
    severity: 'error',
    category: 'system',
    shortDesc: 'Internal Error',
    suggestedAction: 'Try again. If problem persists, contact support.',
  },

  // RAG Errors
  'RAG-AT-TIME-MISSING': {
    severity: 'error',
    category: 'validation',
    shortDesc: 'at_time Parameter Missing',
    suggestedAction: 'Provide the at_time parameter.',
  },
  'RAG-AT-TIME-DRIFT-FORBIDDEN': {
    severity: 'error',
    category: 'validation',
    shortDesc: 'at_time Drift Forbidden',
    suggestedAction: 'Use a fixed ISO-8601 timestamp instead of "latest".',
  },
  'RAG-VALIDATION-ERROR': {
    severity: 'error',
    category: 'validation',
    shortDesc: 'RAG Validation Error',
    suggestedAction: 'Check query/at_time/top_k input parameters.',
  },
  'RAG-INTERNAL-ERROR': {
    severity: 'error',
    category: 'system',
    shortDesc: 'RAG Internal Error',
    suggestedAction: 'Try again. If problem persists, contact support.',
  },

  // Import Errors
  CONSTITUTION_GATE_FAILED: {
    severity: 'error',
    category: 'governance',
    shortDesc: 'Constitution Gate Failed',
    suggestedAction: 'Review required_changes and update skill accordingly.',
  },
  SYSTEM_AUDIT_FAILED: {
    severity: 'error',
    category: 'governance',
    shortDesc: 'System Audit Failed',
    suggestedAction: 'Review L1-L5 audit layers and address gaps.',
  },
  IMPORT_INTERNAL_ERROR: {
    severity: 'error',
    category: 'system',
    shortDesc: 'Import Internal Error',
    suggestedAction: 'Preserve evidence_ref for debugging. Contact support.',
  },
};

// ============================================
// Helper Functions
// ============================================

/**
 * Get error metadata from registry
 */
function getErrorMeta(errorCode: string) {
  return ERROR_CODE_REGISTRY[errorCode] || {
    severity: 'error' as const,
    category: 'system' as const,
    shortDesc: errorCode,
    suggestedAction: 'Contact support for assistance.',
  };
}



/**
 * Get category icon
 */
function getCategoryIcon(category: string): string {
  switch (category) {
    case 'security':
      return '🔒';
    case 'governance':
      return '🚧';
    case 'validation':
      return '⚠️';
    case 'system':
      return '⚙️';
    default:
      return '❌';
  }
}

// ============================================
// Sub-Components
// ============================================

/** Copy to clipboard button */
const CopyButton: React.FC<{ text: string; label?: string }> = ({ text, label = 'Copy' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [text]);

  return (
    <button
      className={styles['copy-btn']}
      onClick={handleCopy}
    >
      {copied ? '✓ Copied' : label}
    </button>
  );
};

/** Evidence reference link */
const EvidenceRef: React.FC<{
  evidenceRef?: string;
  runId: string;
  onEvidenceClick?: (ref: string) => void;
  onRunIdClick?: (id: string) => void;
}> = ({ evidenceRef, runId, onEvidenceClick, onRunIdClick }) => (
  <div className={styles['evidence-trail']}>
    <div className={styles['data-label']}>
      Evidence Trail
    </div>

    <div className={styles['evidence-row']}>
      <span className={styles['data-label']}>run_id:</span>
      <button
        className={`${styles['mono-link']} ${onRunIdClick ? styles['clickable'] : ''}`}
        onClick={() => onRunIdClick?.(runId)}
      >
        {runId}
      </button>
      <CopyButton text={runId} />
    </div>

    {evidenceRef && (
      <div className={styles['evidence-row']}>
        <span className={styles['data-label']}>evidence_ref:</span>
        <button
          className={`${styles['mono-link']} ${onEvidenceClick ? styles['clickable'] : ''}`}
          onClick={() => onEvidenceClick?.(evidenceRef)}
        >
          {evidenceRef}
        </button>
        <CopyButton text={evidenceRef} />
      </div>
    )}
  </div>
);

/** Required changes list */
const RequiredChanges: React.FC<{ changes: string[] }> = ({ changes }) => (
  <div className={styles['required-changes']}>
    <div className={styles['data-label']}>
      Required Changes ({changes.length})
    </div>
    <ul className={styles['changes-list']}>
      {changes.map((change, idx) => (
        <li key={idx} className={styles['change-item']}>
          {change}
        </li>
      ))}
    </ul>
  </div>
);

// ============================================
// Main Component
// ============================================

export function BlockReasonCard({
  errorCode,
  blockedBy,
  message,
  evidenceRef,
  runId,
  requiredChanges,
  suggestedAction,
  forbiddenFieldEvidence,
  context,
  title,
  onEvidenceClick,
  onRunIdClick,
  compact = false,
}: BlockReasonCardProps) {
  const [isExpanded, setIsExpanded] = useState(!compact);

  const errorMeta = getErrorMeta(errorCode);
  const categoryIcon = getCategoryIcon(errorMeta.category);
  const effectiveSuggestion = suggestedAction || errorMeta.suggestedAction;

  // Compact mode: Just show header with expand
  if (compact && !isExpanded) {
    return (
      <button
        className={`${styles.card} ${styles[`severity-${errorMeta.severity}`]} ${styles['flex-center']} ${styles['compact-btn']}`}
        onClick={() => setIsExpanded(true)}
        aria-expanded="false"
      >
        <div className={`${styles.header} ${styles[`header-${errorMeta.severity}`]} ${styles['w-full']}`}>
          <div className={styles['header-title']}>
            <span>{categoryIcon}</span>
            <span>{errorCode}</span>
            <span className={`${styles['data-label']} ${styles['capitalize-none']}`}>{blockedBy}</span>
          </div>
          <span className={styles['data-label']}>Expand Details ▼</span>
        </div>
      </button>
    );
  }

  return (
    <article
      className={`${styles.card} ${styles[`severity-${errorMeta.severity}`]}`}
      role="alert"
      aria-live="assertive"
    >
      {/* Header */}
      <header className={`${styles.header} ${styles[`header-${errorMeta.severity}`]}`}>
        <div className={styles['header-title']}>
          <span aria-hidden="true">{categoryIcon}</span>
          <span>{title || 'Operation Blocked'}</span>
        </div>
        <div className={`${styles['flex-center']} gap-2`}>
          <span className={`${styles['code-badge']} ${styles[`code-badge-${errorMeta.severity}`]}`}>
            {errorCode}
          </span>
          {compact && (
            <button
              onClick={() => setIsExpanded(false)}
              className={`${styles['mono-link']} ${styles['text-secondary']} ${styles['ml-2']}`}
              aria-expanded="true"
            >
              Collapse ▲
            </button>
          )}
        </div>
      </header>

      {/* Body */}
      <div className={styles.body}>

        {/* Interception Conclusion: The most prominent data node */}
        <div className={styles['data-point']}>
          <div className={styles['data-label']}>Blocked By</div>
          <div className={`${styles['data-value-primary']} ${styles[`data-value-${errorMeta.severity}`]}`}>
            {blockedBy}
          </div>
        </div>

        {/* Detailed Message */}
        <div className={styles['message-box']}>
          {message}
        </div>

        {/* Security Warning (for forbidden field injection) */}
        {forbiddenFieldEvidence && (
          <div className={`${styles.card} ${styles['severity-critical']} ${styles['mb-0']}`}>
            <header className={`${styles.header} ${styles['header-critical']}`}>
              <div className={styles['header-title']}>
                <span aria-hidden="true">!</span>
                <span>SECURITY ALERT</span>
              </div>
            </header>
            <div className={`${styles.body} ${styles['bg-base-100']}`}>
              <p className={styles['change-item']}>Forbidden field injection detected. This attempt has been logged.</p>
            </div>
          </div>
        )}

        {/* Required Changes */}
        {requiredChanges && requiredChanges.length > 0 && (
          <RequiredChanges changes={requiredChanges} />
        )}

        {/* Suggested Action */}
        <div className={`${styles['evidence-trail']} ${styles['border-pass']}`}>
          <div className={styles['data-label']}>Suggested Fix</div>
          <div className={`${styles['change-item']} ${styles['text-pass']} ${styles['fw-600']}`}>
            {effectiveSuggestion}
          </div>
        </div>

        {/* Evidence Trail */}
        <EvidenceRef
          evidenceRef={evidenceRef}
          runId={runId}
          onEvidenceClick={onEvidenceClick}
          onRunIdClick={onRunIdClick}
        />

        {/* Context (expandable) */}
        {context && Object.keys(context).length > 0 && (
          <details className={styles['required-changes']}>
            <summary className={`${styles['mono-link']} ${styles['text-secondary']}`}>
              Additional Context
            </summary>
            <pre className={`${styles['message-box']} ${styles['context-pre']}`}>
              {JSON.stringify(context, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </article>
  );
}

// ============================================
// Factory Function for N8nErrorEnvelope
// ============================================

/**
 * Create BlockReasonCard from N8nErrorEnvelope
 */
export function BlockReasonCardFromError(
  error: N8nErrorEnvelope,
  options?: Partial<BlockReasonCardProps>
): React.ReactElement {
  return (
    <BlockReasonCard
      errorCode={error.error_code}
      blockedBy={error.blocked_by}
      message={error.message}
      evidenceRef={error.evidence_ref}
      runId={error.run_id}
      requiredChanges={error.required_changes}
      forbiddenFieldEvidence={error.forbidden_field_evidence}
      {...options}
    />
  );
}

export default BlockReasonCard;
