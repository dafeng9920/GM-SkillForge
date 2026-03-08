/**
 * RagQueryPage - RAG 知识库查询页面
 *
 * 功能:
 * - 查询表单 (query / at_time / repo_url / commit_sha / top_k)
 * - 搜索结果列表 (相关度排序、片段高亮)
 * - 每个命中项显示 evidence_ref
 * - replay_pointer 展示
 * - at_time 漂移错误按 Fail-Closed 展示
 *
 * 约束:
 * - at_time 必须是固定时间戳，禁止 "latest"
 * - RAG 命中项必须显示 evidence_ref
 * - run_id/evidence_ref 可点击跳转
 *
 * @module pages/audit/RagQueryPage
 */

import React, { useState, useCallback } from 'react';
import type { QueryRagResponse, N8nErrorEnvelope, RagResultItem } from '../../types/orchestrationProjection';
import { mockQueryRagAllow } from '../../mocks/orchestrationProjection.mock';
import EvidenceDrawer from '../../components/governance/EvidenceDrawer';

// ============================================
// Types
// ============================================

interface QueryRagParams {
  query: string;
  at_time: string;
  repo_url: string;
  commit_sha: string;
  top_k: number;
}

// at_time 漂移值列表（禁止值）
const DRIFT_VALUES = ['latest', 'now', 'current', 'today'];

// ============================================
// Sub-Components
// ============================================

/**
 * 查询表单组件
 */
const QueryForm: React.FC<{
  params: QueryRagParams;
  onParamChange: (key: keyof QueryRagParams, value: string | number) => void;
  onSearch: () => void;
  onReset: () => void;
  isLoading: boolean;
  atTimeError: string | null;
}> = ({ params, onParamChange, onSearch, onReset, isLoading, atTimeError }) => {
  return (
    <div style={styles.queryForm}>
      <div style={styles.formTitle}>🔍 RAG 知识库查询</div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          query <span style={styles.required}>*</span>
          <textarea
            value={params.query}
            onChange={(e) => onParamChange('query', e.target.value)}
            placeholder="输入查询内容..."
            style={{ ...styles.formTextarea, minHeight: '60px' }}
            rows={2}
          />
        </label>
      </div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          at_time <span style={styles.required}>*</span>
          <input
            type="datetime-local"
            value={params.at_time}
            onChange={(e) => onParamChange('at_time', e.target.value)}
            style={{
              ...styles.formInput,
              borderColor: atTimeError ? '#EF4444' : '#D1D5DB',
            }}
          />
          {atTimeError && (
            <div style={styles.fieldError}>{atTimeError}</div>
          )}
          <div style={styles.fieldHint}>
            必须是固定时间戳，禁止使用 latest/now/current/today
          </div>
        </label>
      </div>

      <div style={styles.formRowInline}>
        <label style={{ ...styles.formLabel, flex: 1 }}>
          repo_url (可选)
          <input
            type="text"
            value={params.repo_url}
            onChange={(e) => onParamChange('repo_url', e.target.value)}
            placeholder="https://github.com/..."
            style={styles.formInput}
          />
        </label>
        <label style={{ ...styles.formLabel, flex: 1 }}>
          commit_sha (可选)
          <input
            type="text"
            value={params.commit_sha}
            onChange={(e) => onParamChange('commit_sha', e.target.value)}
            placeholder="a1b2c3d4..."
            style={styles.formInput}
          />
        </label>
      </div>

      <div style={styles.formRow}>
        <label style={styles.formLabel}>
          top_k (返回结果数)
          <div style={styles.sliderContainer}>
            <input
              type="range"
              min="1"
              max="20"
              value={params.top_k}
              onChange={(e) => onParamChange('top_k', parseInt(e.target.value, 10))}
              style={styles.slider}
            />
            <span style={styles.sliderValue}>{params.top_k}</span>
          </div>
        </label>
      </div>

      <div style={styles.formActions}>
        <button
          onClick={onSearch}
          disabled={isLoading || !!atTimeError}
          style={{
            ...styles.searchButton,
            opacity: isLoading || atTimeError ? 0.6 : 1,
          }}
        >
          {isLoading ? '查询中...' : '搜索'}
        </button>
        <button onClick={onReset} style={styles.resetButton}>
          重置
        </button>
      </div>
    </div>
  );
};

/**
 * 结果项组件
 */
const ResultItem: React.FC<{
  item: RagResultItem;
  index: number;
  query: string;
  onEvidenceClick: (evidenceRef: string) => void;
  runId?: string;
  evidenceRef?: string;
}> = ({ item, index, query, onEvidenceClick, runId, evidenceRef }) => {
  // 高亮匹配文本
  const highlightText = (text: string, queryStr: string) => {
    if (!queryStr.trim()) return text;
    const parts = text.split(new RegExp(`(${queryStr})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === queryStr.toLowerCase()
        ? <mark key={i} style={styles.highlight}>{part}</mark>
        : part
    );
  };

  return (
    <div style={styles.resultItem}>
      <div style={styles.resultHeader}>
        <span style={styles.resultIndex}>#{index + 1}</span>
        <span style={styles.resultScore}>
          相关度: <strong>{(item.score || 0).toFixed(2)}</strong>
        </span>
      </div>
      <div style={styles.resultText}>
        {highlightText(item.text || '', query)}
      </div>
      {item.source && (
        <div style={styles.resultSource}>
          📍 {item.source}
        </div>
      )}
      {/* Evidence Ref 显示 - 关键约束 */}
      <div style={styles.resultEvidence}>
        {runId && (
          <div style={styles.evidenceField}>
            <span style={styles.evidenceLabel}>run_id:</span>
            <span style={styles.evidenceValue}>{runId}</span>
          </div>
        )}
        {evidenceRef && (
          <div style={styles.evidenceField}>
            <span style={styles.evidenceLabel}>evidence_ref:</span>
            <button
              style={styles.evidenceLink}
              onClick={() => onEvidenceClick(evidenceRef!)}
            >
              {evidenceRef}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Replay Pointer 类型定义
 */
interface ReplayPointerType {
  at_time?: string;
  [key: string]: unknown;
}

/**
 * Replay Pointer 展示组件
 */
const ReplayPointerDisplay: React.FC<{
  replayPointer: ReplayPointerType | null | undefined;
}> = ({ replayPointer }) => {
  if (!replayPointer) return null;

  return (
    <div style={styles.replayPointer}>
      <div style={styles.replayPointerTitle}>📍 replay_pointer</div>
      <div style={styles.replayPointerContent}>
        {replayPointer.at_time && (
          <div style={styles.replayPointerField}>
            <span style={styles.replayPointerLabel}>at_time</span>
            <span style={styles.replayPointerValue}>{replayPointer.at_time}</span>
          </div>
        )}
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
  // 特殊处理 at_time 漂移错误
  const isAtTimeDriftError = error.error_code === 'RAG-AT-TIME-DRIFT-FORBIDDEN';

  return (
    <div style={{
      ...styles.errorPanel,
      borderColor: isAtTimeDriftError ? '#F59E0B' : '#FECACA',
      backgroundColor: isAtTimeDriftError ? '#FFFBEB' : '#FEF2F2',
    }}>
      <div style={styles.errorHeader}>
        <span style={styles.errorIcon}>{isAtTimeDriftError ? '⚠️' : '🚫'}</span>
        <span style={{
          ...styles.errorCode,
          color: isAtTimeDriftError ? '#D97706' : '#DC2626',
        }}>
          {error.error_code}
        </span>
      </div>
      <div style={styles.errorContent}>
        {isAtTimeDriftError && (
          <div style={styles.errorHint}>
            <strong>修复建议:</strong> 使用固定 ISO-8601 时间戳替代漂移值
            <br />
            <code style={styles.errorCodeExample}>例如: 2026-02-20T14:30:00Z</code>
          </div>
        )}
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
              style={styles.evidenceLink}
              onClick={() => onEvidenceClick(error.evidence_ref!)}
            >
              {error.evidence_ref}
            </button>
          </div>
        )}
        {error.run_id && (
          <div style={styles.errorField}>
            <span style={styles.errorLabel}>run_id</span>
            <span style={styles.monoValue}>{error.run_id}</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================
// Main Component
// ============================================

export const RagQueryPage: React.FC = () => {
  // State
  const [queryParams, setQueryParams] = useState<QueryRagParams>({
    query: '',
    at_time: '',
    repo_url: '',
    commit_sha: '',
    top_k: 5,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<QueryRagResponse | null>(null);
  const [error, setError] = useState<N8nErrorEnvelope | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerData, setDrawerData] = useState<Record<string, unknown> | null>(null);

  // 验证 at_time 是否有漂移
  const getAtTimeError = useCallback((atTime: string): string | null => {
    const trimmed = atTime.trim().toLowerCase();
    if (DRIFT_VALUES.includes(trimmed)) {
      return `禁止使用漂移值 "${trimmed}"，请使用固定时间戳`;
    }
    return null;
  }, []);

  const atTimeError = queryParams.at_time ? getAtTimeError(queryParams.at_time) : null;

  // Handlers
  const handleParamChange = useCallback((key: keyof QueryRagParams, value: string | number) => {
    setQueryParams(prev => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = useCallback(() => {
    setQueryParams({
      query: '',
      at_time: '',
      repo_url: '',
      commit_sha: '',
      top_k: 5,
    });
    setSearchResult(null);
    setError(null);
  }, []);

  const handleSearch = useCallback(async () => {
    // 验证必填字段
    if (!queryParams.query.trim()) {
      setError({
        ok: false,
        error_code: 'RAG-VALIDATION-ERROR',
        blocked_by: 'VALIDATION',
        message: 'query 字段不能为空',
        run_id: '',
      });
      return;
    }

    if (!queryParams.at_time.trim()) {
      setError({
        ok: false,
        error_code: 'RAG-AT-TIME-MISSING',
        blocked_by: 'VALIDATION',
        message: 'at_time 字段不能为空',
        run_id: '',
      });
      return;
    }

    // 检查 at_time 漂移
    if (atTimeError) {
      setError({
        ok: false,
        error_code: 'RAG-AT-TIME-DRIFT-FORBIDDEN',
        blocked_by: 'BOUNDARY',
        message: atTimeError,
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
      const result = mockQueryRagAllow as QueryRagResponse;
      setSearchResult(result);

      if (!result.ok) {
        setError(result);
      }
    } catch (err) {
      setError({
        ok: false,
        error_code: 'RAG-INTERNAL-ERROR',
        blocked_by: 'NETWORK',
        message: String(err),
        run_id: '',
      });
    } finally {
      setIsLoading(false);
    }
  }, [queryParams, atTimeError]);

  const handleEvidenceClick = useCallback((evidenceRef: string) => {
    // 跳转到 AuditPack 页面查看证据
    console.log('Navigate to /audit/packs with evidence_ref:', evidenceRef);
    // TODO: 实现路由跳转
    // navigate('/audit/packs', { state: { evidence_ref: evidenceRef } });
  }, []);

  const handleViewFullResult = useCallback(() => {
    if (searchResult && searchResult.ok) {
      setDrawerData(searchResult as unknown as Record<string, unknown>);
      setDrawerVisible(true);
    }
  }, [searchResult]);

  // 检查结果是否有效
  const hasResults = searchResult?.ok && searchResult.data?.results && searchResult.data.results.length > 0;

  return (
    <div style={styles.page}>
      {/* Page Header */}
      <header style={styles.pageHeader}>
        <h1 style={styles.pageTitle}>🔍 RAG 知识库查询</h1>
        <div style={styles.pageSubtitle}>Query knowledge base with replay capability</div>
      </header>

      {/* Main Content */}
      <div style={styles.mainContent}>
        {/* Left: Query Form */}
        <div style={styles.leftPanel}>
          <QueryForm
            params={queryParams}
            onParamChange={handleParamChange}
            onSearch={handleSearch}
            onReset={handleReset}
            isLoading={isLoading}
            atTimeError={atTimeError}
          />

          {/* Error Display */}
          {error && (
            <ErrorPanel error={error} onEvidenceClick={handleEvidenceClick} />
          )}
        </div>

        {/* Right: Results */}
        <div style={styles.rightPanel}>
          {/* Results Header */}
          {hasResults && (
            <div style={styles.resultsHeader}>
              <div style={styles.resultsCount}>
                找到 {searchResult!.data!.results!.length} 个相关结果
              </div>
              <button onClick={handleViewFullResult} style={styles.viewJsonButton}>
                📄 查看完整响应
              </button>
            </div>
          )}

          {/* Results List */}
          {hasResults ? (
            <div style={styles.resultsList}>
              {searchResult!.data!.results!.map((item, index) => (
                <ResultItem
                  key={item.id || index}
                  item={item}
                  index={index}
                  query={queryParams.query}
                  onEvidenceClick={handleEvidenceClick}
                  runId={searchResult?.run_id}
                  evidenceRef={searchResult?.evidence_ref}
                />
              ))}

              {/* Replay Pointer */}
              {searchResult!.data!.replay_pointer && (
                <ReplayPointerDisplay replayPointer={searchResult!.data!.replay_pointer} />
              )}
            </div>
          ) : (
            !isLoading && !error && (
              <div style={styles.emptyState}>
                <span style={styles.emptyIcon}>🔍</span>
                <span>输入查询内容开始搜索</span>
                <div style={styles.emptyHints}>
                  <div style={styles.emptyHint}>• at_time 必须使用固定时间戳</div>
                  <div style={styles.emptyHint}>• 支持 repo_url 和 commit_sha 过滤</div>
                  <div style={styles.emptyHint}>• 调整 top_k 控制返回数量</div>
                </div>
              </div>
            )
          )}
        </div>
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer
        visible={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        title="RAG 查询完整响应"
        data={drawerData}
        runId={searchResult?.ok ? searchResult.run_id : undefined}
        evidenceRef={searchResult?.ok ? searchResult.evidence_ref : undefined}
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
    width: '380px',
    minWidth: '300px',
    display: 'flex',
    flexDirection: 'column',
    borderRight: '1px solid #E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  rightPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    minWidth: 0,
    backgroundColor: '#F9FAFB',
  },
  queryForm: {
    padding: '20px',
  },
  formTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1F2937',
    marginBottom: '16px',
  },
  formRow: {
    marginBottom: '16px',
  },
  formRowInline: {
    display: 'flex',
    gap: '12px',
    marginBottom: '16px',
  },
  formLabel: {
    display: 'flex',
    flexDirection: 'column',
    fontSize: '12px',
    fontWeight: 500,
    color: '#6B7280',
    gap: '6px',
  },
  required: {
    color: '#EF4444',
    marginLeft: '2px',
  },
  formInput: {
    marginTop: '4px',
    padding: '10px 12px',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: '#F9FAFB',
  },
  formTextarea: {
    marginTop: '4px',
    padding: '10px 12px',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: '#F9FAFB',
    resize: 'vertical',
  },
  fieldError: {
    marginTop: '4px',
    fontSize: '12px',
    color: '#EF4444',
  },
  fieldHint: {
    marginTop: '4px',
    fontSize: '11px',
    color: '#9CA3AF',
  },
  sliderContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginTop: '4px',
  },
  slider: {
    flex: 1,
    accentColor: '#3B82F6',
  },
  sliderValue: {
    minWidth: '30px',
    textAlign: 'center',
    fontSize: '14px',
    fontWeight: 600,
    color: '#3B82F6',
  },
  formActions: {
    display: 'flex',
    gap: '8px',
    marginTop: '20px',
  },
  searchButton: {
    flex: 1,
    padding: '12px 16px',
    backgroundColor: '#3B82F6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
  },
  resetButton: {
    padding: '12px 16px',
    backgroundColor: '#F3F4F6',
    color: '#6B7280',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  resultsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E5E7EB',
  },
  resultsCount: {
    fontSize: '14px',
    color: '#1F2937',
  },
  viewJsonButton: {
    background: '#F3F4F6',
    border: '1px solid #D1D5DB',
    borderRadius: '6px',
    padding: '6px 12px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  resultsList: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
  },
  resultItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    borderLeft: '3px solid #3B82F6',
  },
  resultHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '12px',
  },
  resultIndex: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#3B82F6',
  },
  resultScore: {
    fontSize: '12px',
    color: '#6B7280',
  },
  resultText: {
    fontSize: '14px',
    color: '#1F2937',
    lineHeight: '1.6',
    marginBottom: '12px',
  },
  highlight: {
    backgroundColor: '#FEF08A',
    padding: '1px 2px',
    borderRadius: '2px',
  },
  resultSource: {
    fontSize: '12px',
    color: '#6B7280',
    fontFamily: "'JetBrains Mono', monospace",
    marginBottom: '8px',
  },
  resultEvidence: {
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid #E5E7EB',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  evidenceField: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  evidenceLabel: {
    fontSize: '11px',
    color: '#9CA3AF',
    textTransform: 'uppercase',
    minWidth: '100px',
  },
  evidenceValue: {
    fontSize: '12px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#6B7280',
  },
  evidenceLink: {
    background: 'none',
    border: 'none',
    color: '#3B82F6',
    fontSize: '12px',
    fontFamily: "'JetBrains Mono', monospace",
    cursor: 'pointer',
    padding: 0,
    textDecoration: 'underline',
  },
  replayPointer: {
    backgroundColor: '#EFF6FF',
    borderRadius: '8px',
    padding: '16px',
    marginTop: '16px',
    border: '1px solid #BFDBFE',
  },
  replayPointerTitle: {
    fontSize: '13px',
    fontWeight: 600,
    color: '#1E40AF',
    marginBottom: '12px',
  },
  replayPointerContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  replayPointerField: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  replayPointerLabel: {
    fontSize: '11px',
    color: '#3B82F6',
    textTransform: 'uppercase',
    minWidth: '80px',
  },
  replayPointerValue: {
    fontSize: '13px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#1F2937',
  },
  emptyState: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#9CA3AF',
    gap: '12px',
    padding: '40px',
  },
  emptyIcon: {
    fontSize: '48px',
  },
  emptyHints: {
    marginTop: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    textAlign: 'left',
  },
  emptyHint: {
    fontSize: '13px',
    color: '#6B7280',
  },
  errorPanel: {
    margin: '16px',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid',
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
    fontFamily: "'JetBrains Mono', monospace",
  },
  errorContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  errorHint: {
    fontSize: '13px',
    color: '#92400E',
    padding: '8px 12px',
    backgroundColor: 'rgba(255,255,255,0.5)',
    borderRadius: '4px',
    marginBottom: '8px',
  },
  errorCodeExample: {
    display: 'inline-block',
    marginTop: '4px',
    backgroundColor: 'rgba(0,0,0,0.1)',
    padding: '2px 6px',
    borderRadius: '3px',
    fontFamily: "'JetBrains Mono', monospace",
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
  monoValue: {
    fontSize: '12px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#7F1D1D',
  },
};

export default RagQueryPage;
