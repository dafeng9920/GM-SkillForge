/**
 * CognitionPanel Component - UI v2 (Dual Chat Mode)
 *
 * Renders the Divergence Window as a chat interface.
 * Features: Chat history, 10D Cognition visualization as context.
 *
 * @module components/CognitionPanel
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  Cognition10dData,
  Dimension,
  DimensionId,
  DIMENSION_LABELS,
  CRITICAL_DIMENSIONS,
  Message,
} from '../store/l4Slice';

// ============================================
// Helper Functions
// ============================================

function getScoreClass(score: number, threshold: number): string {
  if (score >= threshold) return 'l4-accordion__score--ok';
  if (score >= threshold * 0.8) return 'l4-accordion__score--warn';
  return 'l4-accordion__score--err';
}

function isCriticalDimension(dimId: DimensionId): boolean {
  return CRITICAL_DIMENSIONS.includes(dimId);
}

// ============================================
// Sub-Components
// ============================================

const UsageTag: React.FC<{ dimId: DimensionId }> = ({ dimId }) => {
  let label = 'EXEC';
  let color = 'var(--text-3)';

  if (['L1', 'L2'].includes(dimId)) { label = 'STRATEGY'; color = 'var(--accent)'; }
  else if (['L3', 'L5'].includes(dimId)) { label = 'RISK'; color = 'var(--warn)'; }
  else if (['L10'].includes(dimId)) { label = 'AUDIT'; color = 'var(--ok)'; }

  return (
    <span className="l4-chip" style={{
      fontSize: '9px',
      padding: '2px 6px',
      border: `1px solid ${color}`,
      color: color,
      opacity: 0.8
    }}>
      {label}
    </span>
  );
};

interface DimensionAccordionProps {
  dimension: Dimension;
  isExpanded: boolean;
  onToggle: () => void;
}

const DimensionAccordion: React.FC<DimensionAccordionProps> = ({
  dimension,
  isExpanded,
  onToggle,
}) => {
  const isCritical = isCriticalDimension(dimension.dim_id);

  return (
    <div
      className={`l4-accordion ${isExpanded ? 'l4-accordion--expanded' : ''} ${isCritical ? 'l4-accordion--critical' : ''}`}
    >
      <div className="l4-accordion__header" onClick={onToggle}>
        <div className="l4-accordion__left">
          <span className="l4-accordion__id">{dimension.dim_id}</span>
          <UsageTag dimId={dimension.dim_id} />
          <span className="l4-accordion__label">
            {dimension.label || DIMENSION_LABELS[dimension.dim_id]}
          </span>
        </div>
        <div className="l4-accordion__right">
          <span className={`l4-accordion__score ${getScoreClass(dimension.score, dimension.threshold)}`}>
            {dimension.score.toFixed(0)}
          </span>
          <span className={`l4-chip ${dimension.verdict === 'PASS' ? 'l4-chip--ok' : 'l4-chip--err'}`}>
            {dimension.verdict}
          </span>
          <span className="l4-accordion__icon">{isExpanded ? '▼' : '▶'}</span>
        </div>
      </div>
      {isExpanded && (
        <div className="l4-accordion__body">
          <div className="l4-accordion__reason">{dimension.reason}</div>
          {dimension.evidence_refs && dimension.evidence_refs.length > 0 && (
            <div className="l4-mt-2">
              <div className="l4-text-muted" style={{ fontSize: '11px', marginBottom: '4px' }}>EVIDENCE:</div>
              <div className="l4-flex l4-flex--wrap l4-flex--gap-1">
                {dimension.evidence_refs.map(ref => (
                  <span key={ref.ref_id} className="l4-chip">
                    {ref.type}:{ref.ref_id}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const DivergenceMessageList: React.FC<{ messages: Message[]; onInputChange: (val: string) => void }> = ({ messages, onInputChange }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="divergence-message-list" style={{ flex: '1 1 auto', minHeight: 0, overflowY: 'auto', padding: 'var(--space-3)' }} ref={scrollRef}>
      {messages.length === 0 ? (
        <div className="l4-empty-chat">
          <div className="l4-empty__icon">🧠</div>
          <div style={{ marginBottom: '16px' }}>Draft Mode: Free Reasoning</div>
          <div className="l4-empty__prompts" style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', padding: '0 20px' }}>
            <button className="l4-btn l4-btn--outline l4-btn--sm" onClick={() => onInputChange("Analyze the gathered repo context and highlight risks.")}>Analyze Risks</button>
            <button className="l4-btn l4-btn--outline l4-btn--sm" onClick={() => onInputChange("Draft a contract for a new skill capability.")}>Draft Contract</button>
            <button className="l4-btn l4-btn--outline l4-btn--sm" onClick={() => onInputChange("Check if current implementation matches the spec.")}>Check Spec</button>
          </div>
        </div>
      ) : (
        messages.map((msg) => (
          <div key={msg.id} className={`divergence-message ${msg.role}`} style={{ marginBottom: '12px' }}>
            <div className="l4-text-muted" style={{ fontSize: '10px', marginBottom: '2px', textTransform: 'uppercase' }}>{msg.role}</div>
            <div className="l4-message-content" style={{
              background: msg.role === 'user' ? 'rgba(255,255,255,0.05)' : 'rgba(100, 100, 255, 0.1)',
              padding: '8px 12px',
              borderRadius: '4px',
              borderLeft: msg.role === 'assistant' ? '2px solid var(--accent)' : 'none',
              whiteSpace: 'pre-wrap'
            }}>{msg.content}</div>
          </div>
        ))
      )}
    </div>
  );
};

interface DivergenceChatInputProps {
  value: string;
  onChange: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

const DivergenceChatInput: React.FC<DivergenceChatInputProps> = ({ value, onChange, onSend, isLoading }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSend();
      }
    }
  };

  return (
    <div className="divergence-chat-input" style={{ flex: '0 0 auto', padding: 'var(--space-2)', borderTop: '1px solid var(--border)' }}>
      <div className="l4-flex l4-flex--gap-2">
        <textarea
          className="l4-chat-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入发散性指令... (Shift+Enter 换行)"
          disabled={isLoading}
          rows={2}
          style={{ flex: 1, background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', color: 'var(--text-1)', padding: '8px', borderRadius: '4px' }}
        />
        <button
          className="l4-btn l4-btn--primary"
          onClick={onSend}
          disabled={isLoading || !value.trim()}
          style={{ height: 'auto' }}
        >
          ➤
        </button>
      </div>
    </div>
  );
};


export interface CognitionPanelProps {
  // Chat Props
  messages: Message[];
  inputValue: string;
  onInputChange: (val: string) => void;
  onSend: () => void;

  // Existing Props for Display
  cognitionData: Cognition10dData | null;
  isLoading: boolean;
  error: string | null;
}

export const CognitionPanel: React.FC<CognitionPanelProps> = ({
  messages,
  inputValue,
  onInputChange,
  onSend,
  cognitionData,
  isLoading,
  error,
}) => {
  const [expandedDim, setExpandedDim] = useState<DimensionId | null>(null);

  const toggleDim = useCallback((dimId: DimensionId) => {
    setExpandedDim(prev => (prev === dimId ? null : dimId));
  }, []);

  return (
    <div className="l4-panel l4-panel--divergence" style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      {/* 1. Header */}
      <div className="l4-panel__header" style={{ flex: '0 0 auto' }}>
        <div className="l4-panel__title-group">
          <div className="l4-panel__title" style={{ color: 'var(--accent)' }}>Draft Window</div>
          <div className="l4-panel__subtitle">Free reasoning, no direct publish. (Draft)</div>
        </div>
      </div>

      {/* 2. Message List - 这是要拉伸的部分 */}
      <div style={{ flex: '1 1 auto', minHeight: 0, display: 'flex', flexDirection: 'column' }}>
        <DivergenceMessageList messages={messages} onInputChange={onInputChange} />
      </div>

      {/* 3. Input Area */}
      <DivergenceChatInput
        value={inputValue}
        onChange={onInputChange}
        onSend={onSend}
        isLoading={isLoading}
      />

      {/* 4. 10D Context (if available) */}
      {cognitionData && (
        <div className="l4-section" style={{ flex: '0 0 auto', maxHeight: '35%', overflowY: 'auto', borderTop: '1px solid var(--border)' }}>
          <div className="l4-section__title" style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.02)' }}>
            10-Dimensional Context
            <span className="l4-chip" style={{ marginLeft: '8px', fontSize: '10px' }}>
              PASS COUNT: {cognitionData.overall_pass_count}/10
            </span>
          </div>
          {cognitionData.dimensions.map((dim) => (
            <DimensionAccordion
              key={dim.dim_id}
              dimension={dim}
              isExpanded={expandedDim === dim.dim_id}
              onToggle={() => toggleDim(dim.dim_id)}
            />
          ))}
        </div>
      )}

      {error && (
        <div className="l4-alert l4-alert--err l4-m-3" style={{ flex: '0 0 auto' }}>
          <div className="l4-alert__message">{error}</div>
        </div>
      )}
    </div>
  );
};

export default CognitionPanel;
