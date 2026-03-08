/**
 * Pipeline Step Panel - 流水线步骤面板组件
 *
 * 功能描述：
 * - 展示六步流水线的状态进度
 * - 每步 FAIL 时展示 evidence_ref
 * - 提供重试本步/放弃并回滚 两个动作位
 * - 展示 L1-L5 系统审计结果
 *
 * @module components/governance/PipelineStepPanel
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md
 */

import React, { useState, useCallback } from 'react';

// ============================================
// Types
// ============================================

export type PipelineStepStatus = 'PENDING' | 'IN_PROGRESS' | 'PASS' | 'FAIL';
export type AuditLayerStatus = 'PENDING' | 'PASS' | 'FAIL';

export interface PipelineStep {
  id: string;
  name: string;
  description: string;
  status: PipelineStepStatus;
  evidenceRef?: string;
  error?: string;
}

export interface AuditLayer {
  id: string;
  name: string;
  label: string;
  status: AuditLayerStatus;
  score: number;
  threshold?: number;
}

export interface PipelineStepPanelProps {
  steps: PipelineStep[];
  currentStepIndex: number;
  auditLayers: AuditLayer[];
  onRetry: () => void;
  onRollback: () => void;
  isRunning?: boolean;
}

// ============================================
// Sub-Components
// ============================================

const StatusIcon: React.FC<{ status: PipelineStepStatus | AuditLayerStatus }> = ({ status }) => {
  const iconStyle: React.CSSProperties = {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: 600,
    flexShrink: 0,
  };

  switch (status) {
    case 'PASS':
      return (
        <span style={{ ...iconStyle, backgroundColor: '#D1FAE5', color: '#065F46' }}>
          ✓
        </span>
      );
    case 'FAIL':
      return (
        <span style={{ ...iconStyle, backgroundColor: '#FEE2E2', color: '#991B1B' }}>
          ✕
        </span>
      );
    case 'IN_PROGRESS':
      return (
        <span
          style={{
            ...iconStyle,
            backgroundColor: '#DBEAFE',
            color: '#1D4ED8',
            animation: 'pulse 1.5s ease-in-out infinite',
          }}
        >
          ▶
        </span>
      );
    default:
      return (
        <span style={{ ...iconStyle, backgroundColor: '#F3F4F6', color: '#9CA3AF' }}>
          ○
        </span>
      );
  }
};

const AuditScoreBar: React.FC<{ score: number; threshold?: number; status: AuditLayerStatus }> = ({
  score,
  threshold: _threshold = 60,
  status,
}) => {
  // threshold value is available for future use (e.g., visual indicator)
  void _threshold;
  const barStyle: React.CSSProperties = {
    width: '100%',
    height: '6px',
    backgroundColor: '#E5E7EB',
    borderRadius: '3px',
    overflow: 'hidden',
  };

  const fillStyle: React.CSSProperties = {
    width: `${Math.min(score, 100)}%`,
    height: '100%',
    backgroundColor:
      status === 'PASS' ? '#10B981' : status === 'FAIL' ? '#EF4444' : '#9CA3AF',
    transition: 'width 300ms ease-out',
  };

  return (
    <div style={barStyle}>
      <div style={fillStyle} />
    </div>
  );
};

const StepCard: React.FC<{
  step: PipelineStep;
  isCurrent: boolean;
  isLast: boolean;
  onClick?: () => void;
}> = ({ step, isCurrent, isLast, onClick }) => {
  const [expanded, setExpanded] = useState(false);

  const hasDetails = step.status === 'FAIL' || step.status === 'PASS';
  const isClickable = hasDetails && !isLast;

  const cardStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '12px',
    backgroundColor: isCurrent ? '#EFF6FF' : 'transparent',
    borderRadius: '8px',
    cursor: isClickable ? 'pointer' : 'default',
    transition: 'background-color 150ms',
  };

  const handleToggle = useCallback(() => {
    if (isClickable) {
      setExpanded((prev) => !prev);
      onClick?.();
    }
  }, [isClickable, onClick]);

  return (
    <div>
      <div style={cardStyle} onClick={handleToggle}>
        <StatusIcon status={step.status} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 500, color: '#1F2937' }}>{step.name}</span>
            {step.status === 'FAIL' && (
              <span
                style={{
                  fontSize: '11px',
                  padding: '2px 6px',
                  backgroundColor: '#FEE2E2',
                  color: '#991B1B',
                  borderRadius: '4px',
                }}
              >
                失败
              </span>
            )}
            {step.status === 'PASS' && (
              <span
                style={{
                  fontSize: '11px',
                  padding: '2px 6px',
                  backgroundColor: '#D1FAE5',
                  color: '#065F46',
                  borderRadius: '4px',
                }}
              >
                通过
              </span>
            )}
            {isClickable && (
              <span style={{ fontSize: '12px', color: '#9CA3AF' }}>
                {expanded ? '▼' : '▶'}
              </span>
            )}
          </div>
          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
            {step.description}
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && hasDetails && (
        <div
          style={{
            marginLeft: '32px',
            marginTop: '8px',
            padding: '12px',
            backgroundColor: '#F9FAFB',
            borderRadius: '6px',
            borderLeft: '3px solid',
            borderLeftColor: step.status === 'PASS' ? '#10B981' : '#EF4444',
          }}
        >
          {step.evidenceRef && (
            <div style={{ fontSize: '12px', marginBottom: '8px' }}>
              <span style={{ color: '#6B7280' }}>evidence_ref: </span>
              <code
                style={{
                  fontFamily: '"JetBrains Mono", monospace',
                  color: '#1F2937',
                  backgroundColor: '#F3F4F6',
                  padding: '2px 4px',
                  borderRadius: '3px',
                }}
              >
                {step.evidenceRef}
              </code>
            </div>
          )}
          {step.error && (
            <div style={{ fontSize: '12px', color: '#DC2626' }}>
              <strong>错误:</strong> {step.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AuditLayerCard: React.FC<{ layer: AuditLayer }> = ({ layer }) => {
  const cardStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '8px 12px',
    backgroundColor:
      layer.status === 'PASS'
        ? '#F0FDF4'
        : layer.status === 'FAIL'
        ? '#FEF2F2'
        : '#F9FAFB',
    borderRadius: '6px',
    marginBottom: '8px',
  };

  return (
    <div style={cardStyle}>
      <StatusIcon status={layer.status} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '13px', fontWeight: 500, color: '#374151' }}>
            {layer.label}
          </span>
          <span
            style={{
              fontSize: '12px',
              fontWeight: 600,
              color: layer.status === 'PASS' ? '#065F46' : layer.status === 'FAIL' ? '#991B1B' : '#6B7280',
            }}
          >
            {layer.score}
          </span>
        </div>
        <div style={{ marginTop: '6px' }}>
          <AuditScoreBar score={layer.score} threshold={layer.threshold} status={layer.status} />
        </div>
      </div>
    </div>
  );
};

const ActionButtons: React.FC<{
  onRetry: () => void;
  onRollback: () => void;
  isRunning: boolean;
}> = ({ onRetry, onRollback, isRunning }) => {
  const buttonContainerStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    marginTop: '16px',
    padding: '16px',
    backgroundColor: '#FEF2F2',
    borderRadius: '8px',
    border: '1px solid #FECACA',
  };

  const retryButtonStyle: React.CSSProperties = {
    flex: 1,
    padding: '10px 16px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#fff',
    backgroundColor: '#1890FF',
    border: 'none',
    borderRadius: '6px',
    cursor: isRunning ? 'not-allowed' : 'pointer',
    opacity: isRunning ? 0.6 : 1,
    transition: 'background-color 150ms, opacity 150ms',
  };

  const rollbackButtonStyle: React.CSSProperties = {
    flex: 1,
    padding: '10px 16px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#DC2626',
    backgroundColor: '#fff',
    border: '1px solid #DC2626',
    borderRadius: '6px',
    cursor: isRunning ? 'not-allowed' : 'pointer',
    opacity: isRunning ? 0.6 : 1,
    transition: 'background-color 150ms, opacity 150ms',
  };

  return (
    <div style={buttonContainerStyle}>
      <button onClick={onRetry} disabled={isRunning} style={retryButtonStyle}>
        {isRunning ? '处理中...' : '重试本步'}
      </button>
      <button onClick={onRollback} disabled={isRunning} style={rollbackButtonStyle}>
        放弃并回滚
      </button>
    </div>
  );
};

// ============================================
// Main Component
// ============================================

export const PipelineStepPanel: React.FC<PipelineStepPanelProps> = ({
  steps,
  currentStepIndex,
  auditLayers,
  onRetry,
  onRollback,
  isRunning = false,
}) => {
  // Find if any step has failed
  const failedStepIndex = steps.findIndex((step) => step.status === 'FAIL');
  const hasFailed = failedStepIndex >= 0;

  // Check if all steps passed
  const allPassed = steps.every((step) => step.status === 'PASS');

  // Check if currently running
  const isPipelineRunning = currentStepIndex >= 0 || isRunning;

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
  };

  const progressContainerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '4px',
  };

  const stepConnectorStyle: React.CSSProperties = {
    width: '2px',
    height: '24px',
    backgroundColor: '#E5E7EB',
    marginLeft: '29px',
  };

  const auditSectionStyle: React.CSSProperties = {
    marginTop: '20px',
    paddingTop: '16px',
    borderTop: '1px solid #E5E7EB',
  };

  const sectionTitleStyle: React.CSSProperties = {
    fontSize: '14px',
    fontWeight: 600,
    color: '#374151',
    marginBottom: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const emptyStateStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '32px',
    color: '#9CA3AF',
    textAlign: 'center',
  };

  // If pipeline hasn't started
  if (!isPipelineRunning && !hasFailed && !allPassed) {
    return (
      <div style={emptyStateStyle}>
        <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>📦</div>
        <div style={{ fontSize: '14px' }}>填写导入参数并点击"开始导入"</div>
        <div style={{ fontSize: '12px', marginTop: '8px' }}>
          流水线将执行六步治理流程
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Pipeline Steps */}
      <div>
        <div style={sectionTitleStyle}>
          <span>六步流水线</span>
          {allPassed && (
            <span
              style={{
                fontSize: '12px',
                padding: '2px 8px',
                backgroundColor: '#D1FAE5',
                color: '#065F46',
                borderRadius: '4px',
              }}
            >
              全部通过
            </span>
          )}
          {hasFailed && (
            <span
              style={{
                fontSize: '12px',
                padding: '2px 8px',
                backgroundColor: '#FEE2E2',
                color: '#991B1B',
                borderRadius: '4px',
              }}
            >
              已阻塞
            </span>
          )}
        </div>
        <div style={progressContainerStyle}>
          <div style={{ flex: 1 }}>
            {steps.map((step, index) => (
              <React.Fragment key={step.id}>
                <StepCard
                  step={step}
                  isCurrent={index === currentStepIndex}
                  isLast={index === steps.length - 1}
                />
                {index < steps.length - 1 && (
                  <div
                    style={{
                      ...stepConnectorStyle,
                      backgroundColor:
                        step.status === 'PASS'
                          ? '#10B981'
                          : step.status === 'FAIL'
                          ? '#EF4444'
                          : '#E5E7EB',
                    }}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Layers (shown during/after S3) */}
      {(steps[2]?.status === 'IN_PROGRESS' ||
        steps[2]?.status === 'PASS' ||
        steps[2]?.status === 'FAIL') && (
        <div style={auditSectionStyle}>
          <div style={sectionTitleStyle}>
            <span>L1-L5 系统审计</span>
            <span style={{ fontSize: '12px', color: '#6B7280', fontWeight: 400 }}>
              需要 4/5 通过
            </span>
          </div>
          {auditLayers.map((layer) => (
            <AuditLayerCard key={layer.id} layer={layer} />
          ))}
          <div
            style={{
              marginTop: '12px',
              fontSize: '12px',
              color: '#6B7280',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>
              通过: {auditLayers.filter((l) => l.status === 'PASS').length}/5
            </span>
            <span>|</span>
            <span>
              失败: {auditLayers.filter((l) => l.status === 'FAIL').length}/5
            </span>
          </div>
        </div>
      )}

      {/* Action Buttons (shown when failed) */}
      {hasFailed && (
        <ActionButtons
          onRetry={onRetry}
          onRollback={onRollback}
          isRunning={isRunning}
        />
      )}
    </div>
  );
};

export default PipelineStepPanel;

// ============================================
// Styles are inline for component isolation
// ============================================

// Add keyframe animation for pulsing
if (typeof document !== 'undefined') {
  const styleId = 'pipeline-step-panel-styles';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
    `;
    document.head.appendChild(style);
  }
}
