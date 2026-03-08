/**
 * EvidenceDrawer Component
 *
 * 证据 JSON 抽屉组件 - 可复制 JSON 数据
 * 用于显示 run_id、evidence_ref 等审计证据信息
 *
 * @module components/governance/EvidenceDrawer
 */

import React, { useState, useCallback } from 'react';

export interface EvidenceDrawerProps {
  /** 是否显示抽屉 */
  visible: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 抽屉标题 */
  title?: string;
  /** JSON 数据 */
  data: Record<string, unknown> | null;
  /** 运行 ID */
  runId?: string;
  /** 证据引用 */
  evidenceRef?: string;
}

/**
 * 复制到剪贴板功能
 */
const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
};

/**
 * 格式化 JSON 显示
 */
const formatJson = (data: Record<string, unknown> | null): string => {
  if (!data) return '';
  return JSON.stringify(data, null, 2);
};

/**
 * 可复制的字段组件
 */
const CopyableField: React.FC<{
  label: string;
  value: string;
  monospace?: boolean;
}> = ({ label, value, monospace = true }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    const success = await copyToClipboard(value);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [value]);

  return (
    <div style={styles.fieldContainer}>
      <div style={styles.fieldLabel}>{label}</div>
      <div style={styles.fieldValueWrapper}>
        <div style={{
          ...styles.fieldValue,
          fontFamily: monospace ? "'JetBrains Mono', 'Consolas', monospace" : undefined,
        }}>
          {value}
        </div>
        <button
          onClick={handleCopy}
          style={styles.copyButton}
          title={copied ? '已复制!' : '复制'}
        >
          {copied ? '✓' : '📋'}
        </button>
      </div>
    </div>
  );
};

/**
 * 证据抽屉组件
 */
export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  visible,
  onClose,
  title = '证据详情',
  data,
  runId,
  evidenceRef,
}) => {
  const [jsonCopied, setJsonCopied] = useState(false);

  const handleCopyJson = useCallback(async () => {
    if (!data) return;
    const success = await copyToClipboard(formatJson(data));
    if (success) {
      setJsonCopied(true);
      setTimeout(() => setJsonCopied(false), 2000);
    }
  }, [data]);

  if (!visible) return null;

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div
        style={styles.drawer}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.title}>{title}</div>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>

        {/* Key Fields */}
        <div style={styles.content}>
          {runId && (
            <CopyableField label="run_id" value={runId} />
          )}
          {evidenceRef && (
            <CopyableField label="evidence_ref" value={evidenceRef} />
          )}

          {/* JSON Viewer */}
          {data && (
            <div style={styles.jsonSection}>
              <div style={styles.jsonHeader}>
                <span style={styles.jsonTitle}>完整 JSON</span>
                <button
                  onClick={handleCopyJson}
                  style={styles.copyJsonButton}
                >
                  {jsonCopied ? '✓ 已复制' : '📋 复制全部'}
                </button>
              </div>
              <pre style={styles.jsonContent}>
                {formatJson(data)}
              </pre>
            </div>
          )}

          {/* Empty State */}
          {!data && !runId && !evidenceRef && (
            <div style={styles.emptyState}>
              <span style={styles.emptyIcon}>📭</span>
              <span>暂无证据数据</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * 样式定义
 */
const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'flex-end',
    zIndex: 1000,
  },
  drawer: {
    width: '480px',
    maxWidth: '100%',
    height: '100%',
    backgroundColor: '#FFFFFF',
    boxShadow: '-2px 0 8px rgba(0, 0, 0, 0.15)',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    borderBottom: '1px solid #E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  title: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1F2937',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '20px',
    cursor: 'pointer',
    color: '#6B7280',
    padding: '4px 8px',
  },
  content: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
  },
  fieldContainer: {
    marginBottom: '16px',
  },
  fieldLabel: {
    fontSize: '12px',
    fontWeight: 500,
    color: '#6B7280',
    marginBottom: '4px',
    textTransform: 'uppercase',
  },
  fieldValueWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#F3F4F6',
    padding: '8px 12px',
    borderRadius: '6px',
    borderLeft: '3px solid #3B82F6',
  },
  fieldValue: {
    flex: 1,
    fontSize: '13px',
    color: '#1F2937',
    wordBreak: 'break-all',
  },
  copyButton: {
    background: 'none',
    border: '1px solid #D1D5DB',
    borderRadius: '4px',
    padding: '4px 8px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#6B7280',
  },
  jsonSection: {
    marginTop: '24px',
  },
  jsonHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '12px',
  },
  jsonTitle: {
    fontSize: '12px',
    fontWeight: 500,
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  copyJsonButton: {
    background: '#3B82F6',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 12px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 500,
  },
  jsonContent: {
    backgroundColor: '#1F2937',
    color: '#E5E7EB',
    padding: '16px',
    borderRadius: '8px',
    fontSize: '12px',
    fontFamily: "'JetBrains Mono', 'Consolas', monospace",
    overflow: 'auto',
    maxHeight: '400px',
    margin: 0,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 24px',
    color: '#9CA3AF',
    gap: '8px',
  },
  emptyIcon: {
    fontSize: '32px',
  },
};

export default EvidenceDrawer;
