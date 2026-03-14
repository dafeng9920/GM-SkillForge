/**
 * MainChainStatusPanel Component
 *
 * 主链状态面板组件 - 展示完整主链状态和证据入口
 *
 * 用途: TASK-MAIN-04B - 前端承接主链状态、证据入口和运行结果
 *
 * 功能:
 * - 展示主链步骤状态 (Permit -> Pre-Absorb -> Absorb -> Local Accept -> Final Accept)
 * - 提供 Gate Decision 状态展示
 * - 提供证据入口位 (可点击打开 EvidenceDrawer)
 * - 展示运行结果摘要
 */

import React, { useState, useCallback, useMemo } from 'react';
import { EvidenceDrawer } from './EvidenceDrawer';
import type {
  EvidenceEntry,
  MainChainStatus,
  MainChainStep,
  MainChainStepResult,
  RunResult,
} from '../../types/runtimeInterface';
import {
  extractEvidenceEntries,
  getStepDisplayName,
  getStepStatusColor,
  isRunSuccess,
} from '../../types/runtimeInterface';

export interface MainChainStatusPanelProps {
  /** 运行结果 */
  runResult: RunResult;
  /** 主链状态 (可选，如未提供则从 runResult 推导) */
  mainChainStatus?: MainChainStatus;
  /** 是否显示详细信息 */
  showDetails?: boolean;
  /** 步骤顺序 (可自定义) */
  stepOrder?: MainChainStep[];
}

// 默认步骤顺序
const DEFAULT_STEP_ORDER: MainChainStep[] = [
  'permit',
  'pre_absorb_check',
  'absorb',
  'local_accept',
  'final_accept',
];

/**
 * 步骤状态指示器组件
 */
const StepStatusIndicator: React.FC<{
  status: MainChainStepResult['status'];
}> = ({ status }) => {
  const color = getStepStatusColor(status);
  const size = 24;

  let icon: string;
  switch (status) {
    case 'PASS':
      icon = '✓';
      break;
    case 'FAIL':
      icon = '✕';
      break;
    case 'IN_PROGRESS':
      icon = '▶';
      break;
    case 'SKIPPED':
      icon = '⊘';
      break;
    default:
      icon = '○';
  }

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        backgroundColor: color,
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '14px',
        fontWeight: 600,
        flexShrink: 0,
      }}
    >
      {icon}
    </div>
  );
};

/**
 * Gate Decision 标签组件
 */
const GateDecisionTag: React.FC<{
  decision: string;
}> = ({ decision }) => {
  const isAllowed = decision === 'ALLOW';

  return (
    <div
      style={{
        padding: '4px 12px',
        borderRadius: '4px',
        backgroundColor: isAllowed ? '#D1FAE5' : '#FEE2E2',
        color: isAllowed ? '#065F46' : '#991B1B',
        fontSize: '12px',
        fontWeight: 600,
        textTransform: 'uppercase',
        display: 'inline-block',
      }}
    >
      {decision === 'ALLOW' ? '✓ 允许' : decision === 'REQUIRES_CHANGES' ? '⚠ 需要修改' : '✕ 拒绝'}
    </div>
  );
};

/**
 * 主链状态面板组件
 */
export const MainChainStatusPanel: React.FC<MainChainStatusPanelProps> = ({
  runResult,
  mainChainStatus,
  showDetails = true,
  stepOrder = DEFAULT_STEP_ORDER,
}) => {
  // Evidence Drawer 状态
  const [evidenceDrawerVisible, setEvidenceDrawerVisible] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceEntry | null>(null);

  // 推导主链状态 (如果未提供)
  const derivedMainChainStatus = useMemo(() => {
    if (mainChainStatus) return mainChainStatus;
    // 从 runResult 推导简化版本
    const steps: Record<MainChainStep, MainChainStepResult> = {
      permit: { step: 'permit', status: 'PASS' },
      pre_absorb_check: { step: 'pre_absorb_check', status: 'PASS' },
      absorb: {
        step: 'absorb',
        status: isRunSuccess(runResult.status) ? 'PASS' : 'FAIL',
        evidence_ref: runResult.evidence_refs[0]?.source_locator,
        error_message: runResult.error_message,
      },
      local_accept: { step: 'local_accept', status: isRunSuccess(runResult.status) ? 'PASS' : 'PENDING' },
      final_accept: {
        step: 'final_accept',
        status: isRunSuccess(runResult.status) ? 'PASS' : 'FAIL',
        gate_decision: runResult.status === 'success' ? 'ALLOW' : 'DENY',
      },
    };

    return {
      task_id: runResult.task_id,
      run_id: runResult.run_id,
      current_step: 'absorb',
      steps,
      overall_status: runResult.status,
      final_gate_decision: runResult.status === 'success' ? 'ALLOW' : 'DENY',
    };
  }, [runResult, mainChainStatus]);

  // 提取证据入口列表
  const evidenceEntries = useMemo(() => {
    return extractEvidenceEntries(runResult);
  }, [runResult]);

  // 处理证据点击
  const handleEvidenceClick = useCallback((entry: EvidenceEntry) => {
    setSelectedEvidence(entry);
    setEvidenceDrawerVisible(true);
  }, []);

  // 关闭 Evidence Drawer
  const handleCloseEvidenceDrawer = useCallback(() => {
    setEvidenceDrawerVisible(false);
    setSelectedEvidence(null);
  }, []);

  return (
    <div style={styles.container}>
      {/* 头部：任务信息和 Gate Decision */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h3 style={styles.title}>主链状态</h3>
          <div style={styles.metaInfo}>
            <span style={styles.metaItem}>
              <strong>task_id:</strong> {runResult.task_id}
            </span>
            <span style={styles.metaItem}>
              <strong>run_id:</strong> {runResult.run_id}
            </span>
            <span style={styles.metaItem}>
              <strong>executor:</strong> {runResult.executor}
            </span>
          </div>
        </div>
        <div style={styles.headerRight}>
          {derivedMainChainStatus.final_gate_decision && (
            <GateDecisionTag decision={derivedMainChainStatus.final_gate_decision} />
          )}
          <div style={{
            ...styles.statusBadge,
            backgroundColor: isRunSuccess(runResult.status) ? '#D1FAE5' : '#FEE2E2',
            color: isRunSuccess(runResult.status) ? '#065F46' : '#991B1B',
          }}>
            {runResult.status.toUpperCase()}
          </div>
        </div>
      </div>

      {/* 主链步骤展示 */}
      <div style={styles.stepsContainer}>
        {stepOrder.map((stepId, index) => {
          const stepResult = derivedMainChainStatus.steps[stepId];
          if (!stepResult) return null;

          const isLast = index === stepOrder.length - 1;

          return (
            <React.Fragment key={stepId}>
              {/* 步骤卡片 */}
              <div style={styles.stepCard}>
                <div style={styles.stepHeader}>
                  <StepStatusIndicator status={stepResult.status} />
                  <div style={styles.stepInfo}>
                    <div style={styles.stepName}>{getStepDisplayName(stepId)}</div>
                    <div style={styles.stepStatus}>
                      {stepResult.status}
                      {stepResult.gate_decision && ` (${stepResult.gate_decision})`}
                    </div>
                  </div>
                </div>

                {/* 证据入口 */}
                {showDetails && stepResult.evidence_ref && (
                  <div style={styles.evidenceSection}>
                    <div style={styles.evidenceLabel}>证据:</div>
                    <button
                      style={styles.evidenceButton}
                      onClick={() => handleEvidenceClick({
                        type: 'evidence_ref',
                        title: `${getStepDisplayName(stepId)} 证据`,
                        ref: stepResult.evidence_ref!,
                      })}
                    >
                      📄 {stepResult.evidence_ref.split('/').pop()}
                    </button>
                  </div>
                )}

                {/* 错误信息 */}
                {showDetails && stepResult.error_message && (
                  <div style={styles.errorSection}>
                    <div style={styles.errorLabel}>错误:</div>
                    <div style={styles.errorMessage}>{stepResult.error_message}</div>
                  </div>
                )}
              </div>

              {/* 连接线 (不是最后一个步骤) */}
              {!isLast && (
                <div style={styles.stepConnector}>
                  <div style={styles.connectorLine} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* 运行结果摘要 */}
      {showDetails && (
        <div style={styles.summarySection}>
          <h4 style={styles.summaryTitle}>执行摘要</h4>
          <div style={styles.summaryContent}>
            {runResult.summary || '(无摘要)'}
          </div>
          {runResult.executed_commands && runResult.executed_commands.length > 0 && (
            <div style={styles.commandsSection}>
              <div style={styles.commandsLabel}>执行的命令:</div>
              {runResult.executed_commands.map((cmd: string, idx: number) => (
                <code key={idx} style={styles.commandCode}>
                  {cmd}
                </code>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 证据入口区域 */}
      {showDetails && evidenceEntries.length > 0 && (
        <div style={styles.evidenceEntriesSection}>
          <h4 style={styles.evidenceEntriesTitle}>
            证据入口 ({evidenceEntries.length})
          </h4>
          <div style={styles.evidenceEntriesGrid}>
            {evidenceEntries.map((entry: EvidenceEntry, index: number) => (
              <button
                key={index}
                style={styles.evidenceEntryCard}
                onClick={() => handleEvidenceClick(entry)}
              >
                <div style={styles.entryType}>{entry.type}</div>
                <div style={styles.entryTitle}>{entry.title}</div>
                <div style={styles.entryRef}>{entry.ref}</div>
                {entry.content_hash && (
                  <div style={styles.entryHash}>
                    SHA256: {entry.content_hash.slice(0, 16)}...
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ArtifactManifest 展示 */}
      {showDetails && runResult.manifest && (
        <div style={styles.manifestSection}>
          <h4 style={styles.manifestTitle}>工件清单</h4>
          <div style={styles.manifestStats}>
            <div style={styles.manifestStat}>
              <strong>{runResult.manifest.artifacts.length}</strong> 工件
            </div>
            <div style={styles.manifestStat}>
              <strong>{runResult.manifest.evidence.length}</strong> 证据
            </div>
            <button
              style={styles.manifestButton}
              onClick={() => handleEvidenceClick({
                type: 'manifest',
                title: '工件清单 (manifest.json)',
                ref: `${runResult.task_id}/${runResult.run_id}/manifest.json`,
              })}
            >
              查看完整清单
            </button>
          </div>
        </div>
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer
        visible={evidenceDrawerVisible}
        onClose={handleCloseEvidenceDrawer}
        title={selectedEvidence?.title || '证据详情'}
        data={selectedEvidence ? {
          type: selectedEvidence.type,
          ref: selectedEvidence.ref,
          content_hash: selectedEvidence.content_hash,
          size_bytes: selectedEvidence.size_bytes,
        } : null}
        runId={runResult.run_id}
        evidenceRef={selectedEvidence?.ref}
      />
    </div>
  );
};

// =============================================================================
// 样式定义
// =============================================================================

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    padding: '20px',
    backgroundColor: '#FFFFFF',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingBottom: '16px',
    borderBottom: '1px solid #E5E7EB',
  },
  headerLeft: {
    flex: 1,
  },
  headerRight: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: '8px',
  },
  title: {
    margin: 0,
    fontSize: '18px',
    fontWeight: 600,
    color: '#1F2937',
  },
  metaInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    marginTop: '8px',
    fontSize: '13px',
    color: '#6B7280',
  },
  metaItem: {
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
    fontSize: '12px',
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
  },
  stepsContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  stepCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '16px',
    backgroundColor: '#F9FAFB',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
  },
  stepHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  stepInfo: {
    flex: 1,
  },
  stepName: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  stepStatus: {
    fontSize: '12px',
    color: '#6B7280',
    marginTop: '2px',
  },
  evidenceSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    paddingLeft: '36px',
  },
  evidenceLabel: {
    fontSize: '12px',
    color: '#6B7280',
  },
  evidenceButton: {
    padding: '4px 8px',
    backgroundColor: '#DBEAFE',
    color: '#1D4ED8',
    border: '1px solid #93C5FD',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
  },
  errorSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    paddingLeft: '36px',
  },
  errorLabel: {
    fontSize: '12px',
    color: '#EF4444',
    fontWeight: 500,
  },
  errorMessage: {
    fontSize: '12px',
    color: '#991B1B',
    backgroundColor: '#FEE2E2',
    padding: '8px',
    borderRadius: '4px',
  },
  stepConnector: {
    display: 'flex',
    justifyContent: 'center',
    padding: '4px 0',
  },
  connectorLine: {
    width: '2px',
    height: '24px',
    backgroundColor: '#D1D5DB',
  },
  summarySection: {
    padding: '16px',
    backgroundColor: '#F9FAFB',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
  },
  summaryTitle: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  summaryContent: {
    fontSize: '13px',
    color: '#374151',
    lineHeight: '1.6',
  },
  commandsSection: {
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid #E5E7EB',
  },
  commandsLabel: {
    fontSize: '12px',
    color: '#6B7280',
    marginBottom: '8px',
  },
  commandCode: {
    display: 'block',
    padding: '8px',
    backgroundColor: '#1F2937',
    color: '#E5E7EB',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
    marginBottom: '4px',
    overflow: 'auto',
  },
  evidenceEntriesSection: {
    padding: '16px',
    backgroundColor: '#F9FAFB',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
  },
  evidenceEntriesTitle: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  evidenceEntriesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '12px',
  },
  evidenceEntryCard: {
    padding: '12px',
    backgroundColor: '#FFFFFF',
    borderRadius: '6px',
    border: '1px solid #E5E7EB',
    cursor: 'pointer',
    textAlign: 'left',
    transition: 'all 0.2s',
  },
  entryType: {
    fontSize: '10px',
    color: '#6B7280',
    textTransform: 'uppercase',
    marginBottom: '4px',
  },
  entryTitle: {
    fontSize: '13px',
    fontWeight: 500,
    color: '#1F2937',
    marginBottom: '4px',
  },
  entryRef: {
    fontSize: '11px',
    color: '#3B82F6',
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
    wordBreak: 'break-all',
    marginBottom: '4px',
  },
  entryHash: {
    fontSize: '10px',
    color: '#9CA3AF',
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
  },
  manifestSection: {
    padding: '16px',
    backgroundColor: '#F9FAFB',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
  },
  manifestTitle: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  manifestStats: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  manifestStat: {
    fontSize: '13px',
    color: '#374151',
  },
  manifestButton: {
    padding: '6px 12px',
    backgroundColor: '#3B82F6',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 500,
    cursor: 'pointer',
    marginLeft: 'auto',
  },
};

export default MainChainStatusPanel;
