/**
 * Main Chain Step Panel - TASK-MAIN-04A
 *
 * 功能描述：
 * - 展示主链步骤的状态进度
 * - 主链步骤：Permit → pre_absorb_check → absorb → local_accept → final_accept
 * - 每个步骤状态：pending | running | pass | fail | deny
 * - 展示关键证据引用
 * - 支持扩展：可接真实后端数据，当前使用模拟数据映射位
 *
 * @module components/governance/MainChainStepPanel
 * @see docs/2026-03-11/TASK-MAIN-04_前端承接完整链路_任务定义_2026-03-11.md
 */

import React, { useState, useCallback } from 'react';

// ============================================
// Types - 主链步骤类型定义
// ============================================

export type MainChainStepStatus = 'pending' | 'running' | 'pass' | 'fail' | 'deny';

export type MainChainStepId = 'permit' | 'pre_absorb_check' | 'absorb' | 'local_accept' | 'final_accept';

export interface MainChainStep {
  id: MainChainStepId;
  name: string;
  shortLabel: string;
  description: string;
  status: MainChainStepStatus;
  evidenceRef?: string;
  error?: string;
  gateDecision?: 'ALLOW' | 'REQUIRES_CHANGES' | 'DENY';
  startedAt?: string;
  completedAt?: string;
}

export interface MainChainStepPanelProps {
  steps: MainChainStep[];
  runId?: string;
  onStepClick?: (step: MainChainStep) => void;
  onEvidenceClick?: (evidenceRef: string) => void;
}

// ============================================
// Sub-Components - 复用现有 UI 模式
// ============================================

const StatusIcon: React.FC<{ status: MainChainStepStatus; size?: 'sm' | 'md' }> = ({ status, size = 'md' }) => {
  const baseSize = size === 'sm' ? 16 : 20;
  const iconStyle: React.CSSProperties = {
    width: `${baseSize}px`,
    height: `${baseSize}px`,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: size === 'sm' ? '10px' : '12px',
    fontWeight: 600,
    flexShrink: 0,
  };

  switch (status) {
    case 'pass':
      return (
        <span style={{ ...iconStyle, backgroundColor: '#D1FAE5', color: '#065F46' }}>
          ✓
        </span>
      );
    case 'fail':
      return (
        <span style={{ ...iconStyle, backgroundColor: '#FEE2E2', color: '#991B1B' }}>
          ✕
        </span>
      );
    case 'deny':
      return (
        <span style={{ ...iconStyle, backgroundColor: '#FEF3C7', color: '#92400E', border: '1px solid #F59E0B' }}>
          🚫
        </span>
      );
    case 'running':
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

const StatusBadge: React.FC<{ status: MainChainStepStatus }> = ({ status }) => {
  const badgeStyle: React.CSSProperties = {
    fontSize: '11px',
    padding: '2px 8px',
    borderRadius: '4px',
    fontWeight: 500,
  };

  const statusConfig: Record<MainChainStepStatus, { label: string; bg: string; color: string }> = {
    pending: { label: '等待中', bg: '#F3F4F6', color: '#6B7280' },
    running: { label: '执行中', bg: '#DBEAFE', color: '#1D4ED8' },
    pass: { label: '通过', bg: '#D1FAE5', color: '#065F46' },
    fail: { label: '失败', bg: '#FEE2E2', color: '#991B1B' },
    deny: { label: '拒绝', bg: '#FEF3C7', color: '#92400E' },
  };

  const config = statusConfig[status];

  return (
    <span style={{ ...badgeStyle, backgroundColor: config.bg, color: config.color }}>
      {config.label}
    </span>
  );
};

const StepCard: React.FC<{
  step: MainChainStep;
  index: number;
  onClick?: () => void;
  onEvidenceClick?: (evidenceRef: string) => void;
}> = ({ step, index, onClick, onEvidenceClick }) => {
  const [expanded, setExpanded] = useState(false);

  const hasDetails = step.status === 'fail' || step.status === 'deny' || step.status === 'pass';
  const isClickable = hasDetails;

  const cardStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '14px',
    backgroundColor: step.status === 'running' ? '#EFF6FF' : 'transparent',
    borderRadius: '8px',
    cursor: isClickable ? 'pointer' : 'default',
    transition: 'background-color 150ms',
    border: step.status === 'running' ? '1px solid #BFDBFE' : '1px solid transparent',
  };

  const handleToggle = useCallback(() => {
    if (isClickable) {
      setExpanded((prev) => !prev);
      onClick?.();
    }
  }, [isClickable, onClick]);

  const handleEvidenceClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (step.evidenceRef) {
      onEvidenceClick?.(step.evidenceRef);
    }
  }, [step.evidenceRef, onEvidenceClick]);

  const formatTime = (ts?: string) => {
    if (!ts) return null;
    try {
      return new Date(ts).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  return (
    <div>
      <div style={cardStyle} onClick={handleToggle}>
        {/* Step Number Badge */}
        <div style={{
          width: '28px',
          height: '28px',
          borderRadius: '50%',
          backgroundColor: step.status === 'pending' ? '#F3F4F6' : '#EFF6FF',
          border: `2px solid ${step.status === 'pass' ? '#10B981' : step.status === 'running' ? '#3B82F6' : '#E5E7EB'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 600,
          color: step.status === 'pass' ? '#065F46' : '#374151',
          flexShrink: 0,
        }}>
          {index + 1}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Header Row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 500, color: '#1F2937', fontSize: '14px' }}>
              {step.shortLabel}
            </span>
            <StatusBadge status={step.status} />
            {step.gateDecision && (
              <span
                style={{
                  fontSize: '11px',
                  padding: '2px 6px',
                  backgroundColor: step.gateDecision === 'ALLOW'
                    ? '#D1FAE5'
                    : step.gateDecision === 'DENY'
                    ? '#FEE2E2'
                    : '#FEF3C7',
                  color: step.gateDecision === 'ALLOW'
                    ? '#065F46'
                    : step.gateDecision === 'DENY'
                    ? '#991B1B'
                    : '#92400E',
                  borderRadius: '4px',
                }}
              >
                {step.gateDecision}
              </span>
            )}
            {isClickable && (
              <span style={{ fontSize: '12px', color: '#9CA3AF', marginLeft: 'auto' }}>
                {expanded ? '▼' : '▶'}
              </span>
            )}
          </div>

          {/* Description */}
          <div style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>
            {step.description}
          </div>

          {/* Time Info for running/pass steps */}
          {(step.startedAt || step.completedAt) && (
            <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '6px', display: 'flex', gap: '12px' }}>
              {step.startedAt && (
                <span>开始: {formatTime(step.startedAt)}</span>
              )}
              {step.completedAt && (
                <span>完成: {formatTime(step.completedAt)}</span>
              )}
            </div>
          )}
        </div>

        {/* Status Icon on the right */}
        <div style={{ flexShrink: 0 }}>
          <StatusIcon status={step.status} />
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && hasDetails && (
        <div
          style={{
            marginLeft: '40px',
            marginTop: '8px',
            padding: '12px',
            backgroundColor: '#F9FAFB',
            borderRadius: '6px',
            borderLeft: '3px solid',
            borderLeftColor: step.status === 'pass' ? '#10B981' : step.status === 'deny' ? '#F59E0B' : '#EF4444',
          }}
        >
          {/* Evidence Ref */}
          {step.evidenceRef && (
            <div style={{ fontSize: '12px', marginBottom: '8px' }}>
              <span style={{ color: '#6B7280' }}>evidence_ref: </span>
              <code
                style={{
                  fontFamily: '"JetBrains Mono", monospace',
                  color: '#1F2937',
                  backgroundColor: '#F3F4F6',
                  padding: '2px 6px',
                  borderRadius: '3px',
                  fontSize: '11px',
                }}
              >
                {step.evidenceRef}
              </code>
              <button
                onClick={handleEvidenceClick}
                style={{
                  marginLeft: '8px',
                  padding: '2px 6px',
                  fontSize: '11px',
                  backgroundColor: '#EFF6FF',
                  color: '#3B82F6',
                  border: '1px solid #BFDBFE',
                  borderRadius: '3px',
                  cursor: 'pointer',
                }}
              >
                查看
              </button>
            </div>
          )}

          {/* Gate Decision Details */}
          {step.gateDecision && step.status === 'deny' && (
            <div style={{ fontSize: '12px', marginBottom: '8px', color: '#92400E' }}>
              <strong>Gate Decision:</strong> {step.gateDecision}
              <br />
              <span style={{ color: '#6B7280' }}>此步骤被治理网关拒绝，无法继续执行。</span>
            </div>
          )}

          {/* Error Message */}
          {step.error && (
            <div style={{ fontSize: '12px', color: '#DC2626', backgroundColor: '#FEF2F2', padding: '8px', borderRadius: '4px' }}>
              <strong>错误:</strong> {step.error}
            </div>
          )}

          {/* Success Message */}
          {step.status === 'pass' && !step.error && (
            <div style={{ fontSize: '12px', color: '#065F46' }}>
              ✓ 步骤执行成功，所有检查项通过。
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================
// Main Component
// ============================================

export const MainChainStepPanel: React.FC<MainChainStepPanelProps> = ({
  steps,
  runId,
  onStepClick,
  onEvidenceClick,
}) => {
  // Calculate overall status
  const hasRunning = steps.some((s) => s.status === 'running');
  const hasFailed = steps.some((s) => s.status === 'fail');
  const hasDenied = steps.some((s) => s.status === 'deny');
  const allPassed = steps.length > 0 && steps.every((s) => s.status === 'pass');

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #E5E7EB',
  };

  const titleStyle: React.CSSProperties = {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1F2937',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const statusSummaryStyle: React.CSSProperties = {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  };

  const summaryBadgeStyle: React.CSSProperties = {
    fontSize: '12px',
    padding: '4px 10px',
    borderRadius: '6px',
    fontWeight: 500,
  };

  const stepConnectorStyle: React.CSSProperties = {
    width: '2px',
    height: '16px',
    backgroundColor: '#E5E7EB',
    marginLeft: '26px',
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={titleStyle}>
          <span>⚡</span>
          <span>主链执行状态</span>
        </div>
        <div style={statusSummaryStyle}>
          {runId && (
            <span style={{
              ...summaryBadgeStyle,
              backgroundColor: '#F3F4F6',
              color: '#6B7280',
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: '11px',
            }}>
              {runId}
            </span>
          )}
          {allPassed && (
            <span style={{ ...summaryBadgeStyle, backgroundColor: '#D1FAE5', color: '#065F46' }}>
              ✓ 全部通过
            </span>
          )}
          {hasDenied && (
            <span style={{ ...summaryBadgeStyle, backgroundColor: '#FEF3C7', color: '#92400E' }}>
              🚫 已拒绝
            </span>
          )}
          {hasFailed && (
            <span style={{ ...summaryBadgeStyle, backgroundColor: '#FEE2E2', color: '#991B1B' }}>
              ✕ 执行失败
            </span>
          )}
          {hasRunning && (
            <span style={{ ...summaryBadgeStyle, backgroundColor: '#DBEAFE', color: '#1D4ED8' }}>
              ▶ 执行中
            </span>
          )}
        </div>
      </div>

      {/* Steps */}
      <div>
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <StepCard
              step={step}
              index={index}
              onClick={() => onStepClick?.(step)}
              onEvidenceClick={onEvidenceClick}
            />
            {index < steps.length - 1 && (
              <div
                style={{
                  ...stepConnectorStyle,
                  backgroundColor:
                    step.status === 'pass'
                      ? '#10B981'
                      : step.status === 'fail'
                      ? '#EF4444'
                      : step.status === 'deny'
                      ? '#F59E0B'
                      : '#E5E7EB',
                }}
              />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Footer Legend */}
      <div style={{
        marginTop: '16px',
        paddingTop: '12px',
        borderTop: '1px dashed #E5E7EB',
        fontSize: '11px',
        color: '#9CA3AF',
        display: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <StatusIcon status="pending" size="sm" /> 等待中
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <StatusIcon status="running" size="sm" /> 执行中
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <StatusIcon status="pass" size="sm" /> 通过
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <StatusIcon status="fail" size="sm" /> 失败
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <StatusIcon status="deny" size="sm" /> 拒绝
        </span>
      </div>
    </div>
  );
};

// ============================================
// Helper: Generate Mock Main Chain Steps
// ============================================

export const generateMockMainChainSteps = (
  status: 'idle' | 'running' | 'pass' | 'fail' | 'deny'
): MainChainStep[] => {
  const now = Date.now();
  const baseSteps: Omit<MainChainStep, 'status' | 'startedAt' | 'completedAt' | 'evidenceRef' | 'error' | 'gateDecision'>[] = [
    {
      id: 'permit',
      name: 'Permit Check',
      shortLabel: 'Permit',
      description: '执行许可检查：验证命令白名单、N1合规',
    },
    {
      id: 'pre_absorb_check',
      name: 'Pre-Absorb Check',
      shortLabel: 'Pre-Absorb',
      description: '吸收前置检查：验证N2完整性、N3时间窗口',
    },
    {
      id: 'absorb',
      name: 'Absorb',
      shortLabel: 'Absorb',
      description: '吸收：执行技能包加载和任务分发',
    },
    {
      id: 'local_accept',
      name: 'Local Accept',
      shortLabel: 'Local Accept',
      description: '本地验收：验证执行结果和证据快照',
    },
    {
      id: 'final_accept',
      name: 'Final Accept',
      shortLabel: 'Final Accept',
      description: '最终验收：执行最终网关裁决',
    },
  ];

  switch (status) {
    case 'idle':
      return baseSteps.map((step) => ({ ...step, status: 'pending' as const }));

    case 'running':
      return baseSteps.map((step, index) => {
        if (index < 2) {
          return {
            ...step,
            status: 'pass' as const,
            startedAt: new Date(now - 5000 - index * 3000).toISOString(),
            completedAt: new Date(now - 3000 - index * 2000).toISOString(),
            evidenceRef: `evidence/main_chain/${step.id}/pass_${now}.json`,
          };
        } else if (index === 2) {
          return {
            ...step,
            status: 'running' as const,
            startedAt: new Date(now - 2000).toISOString(),
          };
        }
        return { ...step, status: 'pending' as const };
      });

    case 'pass':
      return baseSteps.map((step, index) => ({
        ...step,
        status: 'pass' as const,
        startedAt: new Date(now - 20000 - index * 4000).toISOString(),
        completedAt: new Date(now - 18000 - index * 3000).toISOString(),
        evidenceRef: `evidence/main_chain/${step.id}/pass_${now}.json`,
        gateDecision: index === 4 ? 'ALLOW' : undefined,
      }));

    case 'fail':
      return baseSteps.map((step, index) => {
        if (index < 2) {
          return {
            ...step,
            status: 'pass' as const,
            startedAt: new Date(now - 10000 - index * 3000).toISOString(),
            completedAt: new Date(now - 8000 - index * 2000).toISOString(),
            evidenceRef: `evidence/main_chain/${step.id}/pass_${now}.json`,
          };
        } else if (index === 2) {
          return {
            ...step,
            status: 'fail' as const,
            startedAt: new Date(now - 3000).toISOString(),
            error: '技能包加载失败：找不到指定的 skill manifest 文件',
            evidenceRef: `evidence/main_chain/${step.id}/fail_${now}.json`,
          };
        }
        return { ...step, status: 'pending' as const };
      });

    case 'deny':
      return baseSteps.map((step, index) => {
        if (index < 3) {
          return {
            ...step,
            status: 'pass' as const,
            startedAt: new Date(now - 15000 - index * 4000).toISOString(),
            completedAt: new Date(now - 13000 - index * 3000).toISOString(),
            evidenceRef: `evidence/main_chain/${step.id}/pass_${now}.json`,
          };
        } else if (index === 3) {
          return {
            ...step,
            status: 'deny' as const,
            startedAt: new Date(now - 2000).toISOString(),
            gateDecision: 'DENY',
            evidenceRef: `evidence/main_chain/${step.id}/deny_${now}.json`,
            error: 'Gate Decision: DENY - 本地验收发现证据快照签名不匹配',
          };
        }
        return { ...step, status: 'pending' as const };
      });

    default:
      return baseSteps.map((step) => ({ ...step, status: 'pending' as const }));
  }
};

export default MainChainStepPanel;

// ============================================
// Animation Styles
// ============================================

if (typeof document !== 'undefined') {
  const styleId = 'main-chain-step-panel-styles';
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
