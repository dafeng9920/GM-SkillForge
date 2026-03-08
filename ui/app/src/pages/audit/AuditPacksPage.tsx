/**
 * AuditPacksPage - 审计包浏览页面
 *
 * 功能:
 * - 搜索表单 (run_id / evidence_ref / at_time)
 * - AuditPack 列表视图
 * - 详情面板 (完整 JSON + replay_pointer)
 * - 支持 run_id/evidence_ref 点击跳转
 *
 * 约束:
 * - run_id/evidence_ref 在两页都必须可点击跳转
 * - at_time 漂移错误必须按 Fail-Closed 结构展示
 *
 * @module pages/audit/AuditPacksPage
 */

import React, { useState, useCallback } from 'react';
import type { FetchPackResponse, N8nErrorEnvelope } from '../../types/orchestrationProjection';
import { mockFetchPackAllow } from '../../mocks/orchestrationProjection.mock';
import EvidenceDrawer from '../../components/governance/EvidenceDrawer';

// ============================================
// Types
// ============================================

interface FetchPackParams {
  run_id: string;
  evidence_ref: string;
  at_time: string;
}

interface AuditPackItem {
  run_id: string;
  evidence_ref: string;
  gate_decision: 'ALLOW' | 'BLOCK' | 'DENY' | 'REQUIRES_CHANGES';
  release_allowed: boolean;
  fetched_at: string;
  replay_pointer?: {
    snapshot_ref?: string | null;
    at_time?: string | null;
    revision?: string | null;
    evidence_bundle_ref?: string | null;
  } | null;
  [key: string]: unknown;
}

// ============================================
// Sub-Components
// ============================================

/**
 * 搜索表单组件
 */
const SearchForm: React.FC<{
  params: FetchPackParams;
  onParamChange: (key: keyof FetchPackParams, value: string) => void;
  onSearch: () => void;
  onReset: () => void;
  isLoading: boolean;
}> = ({ params, onParamChange, onSearch, onReset, isLoading }) => {
  return (
    <div style={styles.searchForm}>
      <div style={styles.formTitle}>🔍 查询审计包</div>
      <div style={styles.formHint}>
        run_id 与 evidence_ref 至少填写一个
      </div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          run_id
          <input
            type="text"
            value={params.run_id}
            onChange={(e) => onParamChange('run_id', e.target.value)}
            placeholder="RUN-N8N-xxxx-xxxxxxxx-xxxxxxxx"
            style={styles.formInput}
          />
        </label>
      </div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          evidence_ref
          <input
            type="text"
            value={params.evidence_ref}
            onChange={(e) => onParamChange('evidence_ref', e.target.value)}
            placeholder="EV-N8N-INTENT-xxxx-xxxxxxxx-xxxxxxxx"
            style={styles.formInput}
          />
        </label>
      </div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          at_time
          <input
            type="datetime-local"
            value={params.at_time}
            onChange={(e) => onParamChange('at_time', e.target.value)}
            style={styles.formInput}
          />
        </label>
      </div>

      <div style={styles.formActions}>
        <button
          onClick={onSearch}
          disabled={isLoading}
          style={{
            ...styles.searchButton,
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          {isLoading ? '查询中...' : '查询'}
        </button>
        <button onClick={onReset} style={styles.resetButton}>
          重置
        </button>
      </div>
    </div>
  );
};

/**
 * 状态徽章组件
 */
const StatusBadge: React.FC<{
  gateDecision: 'ALLOW' | 'BLOCK' | 'DENY' | 'REQUIRES_CHANGES';
}> = ({ gateDecision }) => {
  const config: Record<string, { bg: string; color: string }> = {
    ALLOW: { bg: '#D1FAE5', color: '#059669' },
    BLOCK: { bg: '#FEE2E2', color: '#DC2626' },
    DENY: { bg: '#FEE2E2', color: '#DC2626' },
    REQUIRES_CHANGES: { bg: '#FEF3C7', color: '#D97706' },
  };

  const style = config[gateDecision] || config.BLOCK;

  return (
    <span style={{
      ...styles.badge,
      backgroundColor: style.bg,
      color: style.color,
    }}>
      {gateDecision}
    </span>
  );
};

/**
 * 列表项组件
 */
const AuditPackListItem: React.FC<{
  item: AuditPackItem;
  isSelected: boolean;
  onClick: () => void;
  onEvidenceClick: (evidenceRef: string) => void;
}> = ({ item, isSelected, onClick, onEvidenceClick }) => {
  return (
    <div
      style={{
        ...styles.listItem,
        backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
        borderLeft: isSelected ? '3px solid #3B82F6' : '3px solid transparent',
      }}
      onClick={onClick}
    >
      <div style={styles.listItemHeader}>
        <span style={styles.listItemId}>{item.run_id.slice(0, 20)}...</span>
        <StatusBadge gateDecision={item.gate_decision} />
      </div>
      <div style={styles.listItemMeta}>
        <span style={styles.listItemDate}>{item.fetched_at}</span>
      </div>
      <div style={styles.listItemEvidence}>
        <button
          style={styles.evidenceLink}
          onClick={(e) => {
            e.stopPropagation();
            onEvidenceClick(item.evidence_ref);
          }}
        >
          📎 {item.evidence_ref.slice(0, 25)}...
        </button>
      </div>
    </div>
  );
};

/**
 * 详情面板组件
 */
const DetailPanel: React.FC<{
  item: AuditPackItem | null;
  onEvidenceClick: (evidenceRef: string) => void;
  onViewFullJson: () => void;
}> = ({ item, onEvidenceClick, onViewFullJson }) => {
  if (!item) {
    return (
      <div style={styles.detailPanel}>
        <div style={styles.detailEmpty}>
          <span style={styles.detailEmptyIcon}>📋</span>
          <span>选择左侧列表项查看详情</span>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.detailPanel}>
      <div style={styles.detailHeader}>
        <h3 style={styles.detailTitle}>审计包详情</h3>
        <button onClick={onViewFullJson} style={styles.viewJsonButton}>
          📄 查看完整 JSON
        </button>
      </div>

      <div style={styles.detailContent}>
        {/* 核心信息 */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>核心标识</div>
          <div style={styles.fieldRow}>
            <span style={styles.fieldName}>run_id</span>
            <span style={styles.fieldValueMono}>{item.run_id}</span>
          </div>
          <div style={styles.fieldRow}>
            <span style={styles.fieldName}>evidence_ref</span>
            <button
              style={styles.evidenceLinkInline}
              onClick={() => onEvidenceClick(item.evidence_ref)}
            >
              {item.evidence_ref}
            </button>
          </div>
        </div>

        {/* 决策信息 */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>决策结果</div>
          <div style={styles.fieldRow}>
            <span style={styles.fieldName}>gate_decision</span>
            <StatusBadge gateDecision={item.gate_decision} />
          </div>
          <div style={styles.fieldRow}>
            <span style={styles.fieldName}>release_allowed</span>
            <span style={{
              ...styles.fieldValue,
              color: item.release_allowed ? '#059669' : '#DC2626',
            }}>
              {item.release_allowed ? '✓ true' : '✗ false'}
            </span>
          </div>
        </div>

        {/* Replay Pointer */}
        {item.replay_pointer && (
          <div style={styles.detailSection}>
            <div style={styles.sectionTitle}>Replay Pointer</div>
            {item.replay_pointer.snapshot_ref && (
              <div style={styles.fieldRow}>
                <span style={styles.fieldName}>snapshot_ref</span>
                <span style={styles.fieldValueMono}>{item.replay_pointer.snapshot_ref}</span>
              </div>
            )}
            {item.replay_pointer.at_time && (
              <div style={styles.fieldRow}>
                <span style={styles.fieldName}>at_time</span>
                <span style={styles.fieldValueMono}>{item.replay_pointer.at_time}</span>
              </div>
            )}
            {item.replay_pointer.revision && (
              <div style={styles.fieldRow}>
                <span style={styles.fieldName}>revision</span>
                <span style={styles.fieldValueMono}>{item.replay_pointer.revision}</span>
              </div>
            )}
          </div>
        )}

        {/* 时间戳 */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>时间信息</div>
          <div style={styles.fieldRow}>
            <span style={styles.fieldName}>fetched_at</span>
            <span style={styles.fieldValue}>{item.fetched_at}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 错误面板 - Fail-Closed 结构展示
 */
const ErrorPanel: React.FC<{
  error: N8nErrorEnvelope;
  onEvidenceClick: (evidenceRef: string) => void;
}> = ({ error, onEvidenceClick }) => {
  return (
    <div style={styles.errorPanel}>
      <div style={styles.errorHeader}>
        <span style={styles.errorIcon}>🚫</span>
        <span style={styles.errorCode}>{error.error_code}</span>
      </div>
      <div style={styles.errorContent}>
        <div style={styles.errorField}>
          <span style={styles.errorLabel}>blocked_by</span>
          <span style={styles.errorValue}>{error.blocked_by}</span>
        </div>
        <div style={styles.errorField}>
          <span style={styles.errorLabel}>message</span>
          <span style={styles.errorValue}>{error.message}</span>
        </div>
        {error.evidence_ref && (
          <div style={styles.errorField}>
            <span style={styles.errorLabel}>evidence_ref</span>
            <button
              style={styles.evidenceLinkInline}
              onClick={() => onEvidenceClick(error.evidence_ref!)}
            >
              {error.evidence_ref}
            </button>
          </div>
        )}
        {error.run_id && (
          <div style={styles.errorField}>
            <span style={styles.errorLabel}>run_id</span>
            <span style={styles.fieldValueMono}>{error.run_id}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================
// Main Component
// ============================================

export const AuditPacksPage: React.FC = () => {
  // State
  const [searchParams, setSearchParams] = useState<FetchPackParams>({
    run_id: '',
    evidence_ref: '',
    at_time: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [, setSearchResult] = useState<FetchPackResponse | null>(null);
  const [error, setError] = useState<N8nErrorEnvelope | null>(null);
  const [selectedItem, setSelectedItem] = useState<AuditPackItem | null>(null);
  const [auditPacks, setAuditPacks] = useState<AuditPackItem[]>([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerData, setDrawerData] = useState<Record<string, unknown> | null>(null);

  // Handlers
  const handleParamChange = useCallback((key: keyof FetchPackParams, value: string) => {
    setSearchParams(prev => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = useCallback(() => {
    setSearchParams({ run_id: '', evidence_ref: '', at_time: '' });
    setSearchResult(null);
    setError(null);
    setAuditPacks([]);
    setSelectedItem(null);
  }, []);

  const handleSearch = useCallback(async () => {
    // 验证至少有一个标识
    if (!searchParams.run_id && !searchParams.evidence_ref) {
      setError({
        ok: false,
        error_code: 'N8N_MISSING_IDENTIFIER',
        blocked_by: 'VALIDATION',
        message: 'run_id 与 evidence_ref 至少填写一个',
        run_id: '',
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 800));

      // 使用 Mock 数据
      const result = mockFetchPackAllow as FetchPackResponse;
      setSearchResult(result);

      if (result.ok) {
        const newItem: AuditPackItem = {
          run_id: result.data.run_id,
          evidence_ref: result.data.evidence_ref,
          gate_decision: result.gate_decision,
          release_allowed: result.release_allowed,
          fetched_at: result.data.fetched_at || new Date().toISOString(),
          replay_pointer: result.data.replay_pointer,
        };

        setAuditPacks([newItem]);
        setSelectedItem(newItem);
      } else {
        setError(result);
      }
    } catch (err) {
      setError({
        ok: false,
        error_code: 'N8N_INTERNAL_ERROR',
        blocked_by: 'NETWORK',
        message: String(err),
        run_id: '',
      });
    } finally {
      setIsLoading(false);
    }
  }, [searchParams]);

  const handleEvidenceClick = useCallback((evidenceRef: string) => {
    // 跳转到 RAG 查询页面并带上 evidence_ref
    console.log('Navigate to /audit/rag-query with evidence_ref:', evidenceRef);
    // TODO: 实现路由跳转
    // navigate('/audit/rag-query', { state: { evidence_ref: evidenceRef } });
  }, []);

  const handleViewFullJson = useCallback(() => {
    if (selectedItem) {
      setDrawerData(selectedItem as unknown as Record<string, unknown>);
      setDrawerVisible(true);
    }
  }, [selectedItem]);

  return (
    <div style={styles.page}>
      {/* Page Header */}
      <header style={styles.pageHeader}>
        <h1 style={styles.pageTitle}>📋 审计包浏览</h1>
        <div style={styles.pageSubtitle}>AuditPack Browser</div>
      </header>

      {/* Main Content */}
      <div style={styles.mainContent}>
        {/* Left: Search + List */}
        <div style={styles.leftPanel}>
          <SearchForm
            params={searchParams}
            onParamChange={handleParamChange}
            onSearch={handleSearch}
            onReset={handleReset}
            isLoading={isLoading}
          />

          {/* Error Display */}
          {error && (
            <ErrorPanel error={error} onEvidenceClick={handleEvidenceClick} />
          )}

          {/* List */}
          <div style={styles.listContainer}>
            <div style={styles.listHeader}>
              审计包列表 ({auditPacks.length})
            </div>
            {auditPacks.length === 0 && !isLoading ? (
              <div style={styles.listEmpty}>
                <span style={styles.listEmptyIcon}>📭</span>
                <span>暂无数据，请先查询</span>
              </div>
            ) : (
              <div style={styles.list}>
                {auditPacks.map((item) => (
                  <AuditPackListItem
                    key={item.run_id}
                    item={item}
                    isSelected={selectedItem?.run_id === item.run_id}
                    onClick={() => setSelectedItem(item)}
                    onEvidenceClick={handleEvidenceClick}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Detail Panel */}
        <DetailPanel
          item={selectedItem}
          onEvidenceClick={handleEvidenceClick}
          onViewFullJson={handleViewFullJson}
        />
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        title="审计包完整数据"
        data={drawerData}
        runId={selectedItem?.run_id}
        evidenceRef={selectedItem?.evidence_ref}
      />
    </div>
  );
};

// ============================================
// Styles
// ============================================

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: '#F5F7FA',
  },
  pageHeader: {
    padding: '20px 24px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E5E7EB',
  },
  pageTitle: {
    fontSize: '24px',
    fontWeight: 600,
    color: '#1F2937',
    margin: 0,
  },
  pageSubtitle: {
    fontSize: '14px',
    color: '#6B7280',
    marginTop: '4px',
  },
  mainContent: {
    display: 'flex',
    flex: 1,
    minHeight: 0,
  },
  leftPanel: {
    width: '400px',
    minWidth: '300px',
    display: 'flex',
    flexDirection: 'column',
    borderRight: '1px solid #E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  searchForm: {
    padding: '16px',
    borderBottom: '1px solid #E5E7EB',
  },
  formTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
    marginBottom: '8px',
  },
  formHint: {
    fontSize: '12px',
    color: '#9CA3AF',
    marginBottom: '12px',
  },
  formRow: {
    marginBottom: '12px',
  },
  formLabel: {
    display: 'flex',
    flexDirection: 'column',
    fontSize: '12px',
    fontWeight: 500,
    color: '#6B7280',
    gap: '4px',
  },
  formInput: {
    marginTop: '4px',
    padding: '8px 12px',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: '#F9FAFB',
  },
  formActions: {
    display: 'flex',
    gap: '8px',
    marginTop: '16px',
  },
  searchButton: {
    flex: 1,
    padding: '10px 16px',
    backgroundColor: '#3B82F6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  resetButton: {
    padding: '10px 16px',
    backgroundColor: '#F3F4F6',
    color: '#6B7280',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  listContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    minHeight: 0,
  },
  listHeader: {
    padding: '12px 16px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#6B7280',
    backgroundColor: '#F9FAFB',
    borderBottom: '1px solid #E5E7EB',
  },
  listEmpty: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#9CA3AF',
    gap: '8px',
  },
  listEmptyIcon: {
    fontSize: '32px',
  },
  list: {
    flex: 1,
    overflow: 'auto',
  },
  listItem: {
    padding: '12px 16px',
    borderBottom: '1px solid #E5E7EB',
    cursor: 'pointer',
    transition: 'background-color 0.15s',
  },
  listItemHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  listItemId: {
    fontSize: '13px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#1F2937',
  },
  listItemMeta: {
    marginBottom: '4px',
  },
  listItemDate: {
    fontSize: '12px',
    color: '#9CA3AF',
  },
  listItemEvidence: {
    marginTop: '4px',
  },
  evidenceLink: {
    background: 'none',
    border: 'none',
    color: '#3B82F6',
    fontSize: '12px',
    cursor: 'pointer',
    padding: 0,
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 600,
  },
  detailPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    minWidth: 0,
  },
  detailEmpty: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#9CA3AF',
    gap: '12px',
  },
  detailEmptyIcon: {
    fontSize: '48px',
  },
  detailHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    borderBottom: '1px solid #E5E7EB',
  },
  detailTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1F2937',
    margin: 0,
  },
  viewJsonButton: {
    background: '#F3F4F6',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    padding: '6px 12px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  detailContent: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
  },
  detailSection: {
    marginBottom: '24px',
  },
  sectionTitle: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#6B7280',
    textTransform: 'uppercase',
    marginBottom: '12px',
    paddingBottom: '8px',
    borderBottom: '1px solid #E5E7EB',
  },
  fieldRow: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
  },
  fieldName: {
    width: '140px',
    fontSize: '13px',
    color: '#6B7280',
  },
  fieldValue: {
    fontSize: '13px',
    color: '#1F2937',
  },
  fieldValueMono: {
    fontSize: '13px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#1F2937',
  },
  evidenceLinkInline: {
    background: 'none',
    border: 'none',
    color: '#3B82F6',
    fontSize: '13px',
    fontFamily: "'JetBrains Mono', monospace",
    cursor: 'pointer',
    padding: 0,
    textDecoration: 'underline',
  },
  errorPanel: {
    margin: '16px',
    padding: '16px',
    backgroundColor: '#FEF2F2',
    borderRadius: '8px',
    border: '1px solid #FECACA',
  },
  errorHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
  },
  errorIcon: {
    fontSize: '20px',
  },
  errorCode: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#DC2626',
    fontFamily: "'JetBrains Mono', monospace",
  },
  errorContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  errorField: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  errorLabel: {
    fontSize: '11px',
    color: '#991B1B',
    textTransform: 'uppercase',
  },
  errorValue: {
    fontSize: '13px',
    color: '#7F1D1D',
  },
};

export default AuditPacksPage;
