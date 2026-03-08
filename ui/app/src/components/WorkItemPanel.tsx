/**
 * WorkItemPanel Component - UI v3 (MVP Polish)
 *
 * Implements the "Work Pane" with:
 * 1. "Three-Piece Set" Header (Permit, Gate, Artifacts).
 * 2. Specialized Empty State (Adopt/Import).
 * 3. Run/Validate Input Area.
 *
 * @module components/WorkItemPanel
 */

import React, { useEffect, useRef } from 'react';
import {
  WorkItem,
  Message,
} from '../store/l4Slice';

export interface WorkItemPanelProps {
  // Chat Props
  workMessages: Message[];
  workInput: string;
  workSending?: boolean;
  onWorkInputChange: (v: string) => void;
  onWorkSend: () => void;

  // Adoption
  onAdopt?: () => void;
  canAdopt?: boolean;

  // Governance Status (Display)
  permitStatus?: string;      // e.g. VALID / INVALID / NONE
  gateDecision?: string;      // e.g. ALLOW / BLOCK
  replayPointer?: string;     // e.g. replay://...

  // Structured Context (Post-Adopt)
  workItem?: WorkItem | null;

  // Execution & Receipt
  onExecute?: () => void;
  executeDisabled?: boolean;
  receiptText?: string;

  // Blocking Visualization
  blockedCode?: string | null;
  blockedReason?: string;

  // Legacy props support
  isLoading?: boolean;
  error?: string | null;
}

// --- Sub-Components (Local for MVP) ---

const WorkHeader: React.FC<{
  permitStatus: string;
  gateDecision: string;
  hasWorkItem: boolean;
}> = ({ permitStatus, gateDecision, hasWorkItem }) => {
  return (
    <div className="work-header-dashboard" style={{ padding: '0 16px 12px', borderBottom: '1px solid var(--panel-border)', background: 'rgba(19, 29, 54, 0.6)', backdropFilter: 'blur(12px)' }}>
      {/* Three Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr 1fr', gap: '8px' }}>

        {/* 1. Permit Card */}
        <div className="l4-card-mini">
          <div className="l4-card-mini__label">PERMIT</div>
          <div className={`l4-card-mini__value ${permitStatus === 'GRANTED' ? 'ok' : 'warn'}`}>
            {permitStatus === 'GRANTED' ? 'PASS' : permitStatus}
          </div>
        </div>

        {/* 2. Gate Progress Card */}
        <div className="l4-card-mini">
          <div className="l4-card-mini__label">GATE PROGRESS</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div className="l4-progress-track" style={{ flex: 1, height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
              <div className="l4-progress-fill" style={{
                width: gateDecision === 'ALLOWED' ? '100%' : (hasWorkItem ? '40%' : '0%'),
                height: '100%',
                background: gateDecision === 'ALLOWED' ? 'var(--ok)' : 'var(--accent)',
                borderRadius: '2px'
              }}></div>
            </div>
            <span className="l4-card-mini__sub" style={{ fontSize: '10px' }}>
              {gateDecision === 'ALLOWED' ? '8/8' : (hasWorkItem ? 'Running...' : '0/8')}
            </span>
          </div>
        </div>

        {/* 3. Artifacts Card */}
        <div className="l4-card-mini">
          <div className="l4-card-mini__label">ARTIFACTS</div>
          <div className="l4-card-mini__value" style={{ fontSize: '11px', color: hasWorkItem ? 'var(--text-1)' : 'var(--text-3)' }}>
            {hasWorkItem ? 'L3 AuditPack' : 'None'}
          </div>
        </div>

      </div>
    </div>
  );
};

const WorkEmptyState: React.FC<{ onAdopt?: () => void; canAdopt?: boolean }> = ({ onAdopt, canAdopt }) => (
  <div className="l4-empty-chat">
    <div className="l4-empty__icon">📋</div>
    <div style={{ marginBottom: '24px', fontSize: '14px', color: 'var(--text-2)' }}>Work Window: Gate/Permit Constrained</div>

    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '280px' }}>
      <button
        className="l4-btn l4-btn--primary"
        onClick={onAdopt}
        disabled={!canAdopt}
        style={{ height: '40px', justifyContent: 'center' }}
      >
        {canAdopt ? '⚡ Generate Contract from Draft' : 'Waiting for Draft...'}
      </button>

      <button
        className="l4-btn l4-btn--outline"
        disabled={true}
        style={{ height: '36px', justifyContent: 'center', opacity: 0.6 }}
      >
        📥 Import AuditRequest
      </button>
    </div>
  </div>
);


export default function WorkItemPanel(props: WorkItemPanelProps) {
  const {
    workMessages,
    workInput,
    workSending = false,
    onWorkInputChange,
    onWorkSend,
    permitStatus = "NONE",
    gateDecision = "IDLE",
    replayPointer = "-",
    workItem = null,
    onExecute,
    executeDisabled = false,
    receiptText = "",
    blockedCode,
    blockedReason,
    onAdopt,
    canAdopt = false,
  } = props;

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of message list
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current;
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }, [workMessages, workItem, receiptText, blockedCode]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      // In Work Window: Input is for "Wait/Human input" or "Validate". 
      // Main action is "Run" via button. 
      // User requested: "Validate" (Secondary).
    }
  };

  return (
    <section className="panel-root work-panel">
      {/* 1) Header Fixed Area */}
      <header className="panel-header" style={{ borderBottom: 'none', paddingBottom: 0 }}>
        <div className="panel-title-wrap">
          <h3 className="panel-title" style={{ color: 'var(--text-1)' }}>Work Window</h3>
          <p className="panel-subtitle">Gate/Permit constrained, producible. (Work)</p>
        </div>
      </header>

      {/* 2) Three-Piece Set Dashboard */}
      <WorkHeader
        permitStatus={permitStatus}
        gateDecision={gateDecision}
        hasWorkItem={!!workItem}
      />

      {/* 3) Body Scrollable Area */}
      <div className="panel-scroll" ref={scrollRef}>

        {/* Blocking Alert */}
        {blockedCode && (
          <div className={`blocking-banner ${String(blockedCode).toLowerCase()}`}>
            <strong>Blockage Detected: {blockedCode}</strong>
            <span>{blockedReason || "执行被治理规则阻断"}</span>
          </div>
        )}

        {/* Message Stream or Empty State */}
        {workMessages.length === 0 ? (
          <WorkEmptyState onAdopt={onAdopt} canAdopt={canAdopt} />
        ) : (
          <div className="work-message-list">
            {workMessages.map((m) => (
              <article key={m.id} className={`work-message ${m.role}`}>
                <div className="work-message__role">{m.role}</div>
                <div className="l4-message-content" style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                {m.timestamp ? <time className="msg-time">{new Date(m.timestamp).toLocaleTimeString()}</time> : null}
              </article>
            ))}
          </div>
        )}

        {/* Receipt (if exists) */}
        {receiptText && receiptText !== "" && (
          <section className="work-receipt" style={{ marginTop: '16px' }}>
            <div className="section-title">Execution Receipt</div>
            <pre className="receipt-terminal">{receiptText}</pre>
          </section>
        )}
      </div>

      {/* 4) Input Fixed Area (WorkComposer) */}
      <footer className="panel-inputbar">
        {/* Input for parameters/context */}
        <textarea
          value={workInput}
          onChange={(e) => onWorkInputChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={blockedCode ? "Blockage detected. View required changes." : `输入参数或调整... (Replay: ${replayPointer})`}
          rows={1}
          className="work-input"
          disabled={workSending || !!blockedCode}
        />

        {/* Run / Validate Actions */}
        <div className="input-actions" style={{ flexDirection: 'row', gap: '8px', minWidth: '160px' }}>
          <button
            type="button"
            className="l4-btn l4-btn--secondary"
            style={{ flex: 1, background: 'var(--panel-2)', border: '1px solid var(--line)' }}
            onClick={onWorkSend} // "Validate" maps to regular send for now (simulate)
            disabled={workSending || !!blockedCode}
          >
            Validate
          </button>

          <button
            type="button"
            className="l4-btn l4-btn--primary"
            style={{ flex: 1.5, fontWeight: 700, background: 'var(--accent)' }}
            onClick={onExecute}
            disabled={executeDisabled || !!blockedCode}
          >
            {workSending ? "Running..." : "Run"}
          </button>
        </div>
      </footer>
    </section>
  );
}
