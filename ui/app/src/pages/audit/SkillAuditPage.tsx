/**
 * SkillAuditPage - P1-1 审计结果页 MVP
 *
 * 功能:
 * - 总览卡: run_date, sample_size, gate_counts, avg_overall_score
 * - 明细表: 按域/技能展示审计结果，支持排序
 * - 结论限制区: policy_version, policy_path, limitations
 * - 读取 reports/skill-audit/*.json 真实数据
 * - P1-2: 加载前 JSON Schema 校验，字段缺失显示可读错误
 *
 * 约束:
 * - 桌面/移动端可用
 * - 支持按 Gate/Score/Domain 排序
 * - 不得用假数据替代真实 JSON
 * - 不得静默吞掉校验失败
 *
 * @module pages/audit/SkillAuditPage
 * @see docs/2026-02-22/tasks/T54_Kior-A.md
 * @see docs/2026-02-22/tasks/T55_vs--cc1.md
 * @see schemas/skill_audit_report.schema.json
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';

// ============================================
// Types
// ============================================

/** Layer status types */
type LayerStatus = 'PASS' | 'WARN' | 'FAIL';

/** Layer scores structure */
interface LayerScores {
  L1_cost: number;
  L2_redundancy: number;
  L3_safety: number;
  L4_structure: number;
  L5_evidence_ready: number;
}

/** Layer status structure */
interface LayerStatusMap {
  L1_cost: LayerStatus;
  L2_redundancy: LayerStatus;
  L3_safety: LayerStatus;
  L4_structure: LayerStatus;
  L5_evidence_ready: LayerStatus;
}

/** Single audit result item */
interface AuditResultItem {
  domain: string;
  skill: string;
  path: string;
  source_sha256: string;
  evidence_ref: string;
  chars: number;
  est_tokens: number;
  repeat_ratio: number;
  broken_links: number;
  checklist_items: number;
  numbered_steps: number;
  tables: number;
  sensitive_hits: number;
  has_disclaimer: boolean;
  has_review_warning: boolean;
  layer_scores: LayerScores;
  layer_status: LayerStatusMap;
  overall_score: number;
  gate: 'PASS' | 'WARN' | 'FAIL';
}

/** Summary structure */
interface AuditSummary {
  run_date: string;
  generated_at: string;
  profile: string;
  policy_version: string;
  policy_path: string;
  scope: string;
  run_id: string;
  evidence_ref: string;
  input_hash: string;
  sample_size: number;
  gate_counts: {
    PASS: number;
    WARN: number;
    FAIL: number;
  };
  avg_overall_score: number;
  avg_est_tokens: number;
  high_cost_count_ge_3000_tokens: number;
  high_redundancy_count_ge_0_26: number;
  result_hash: string;
}

/** Full audit report structure */
interface AuditReport {
  summary: AuditSummary;
  results: AuditResultItem[];
}

/** Sort key types */
type SortKey = 'domain' | 'skill' | 'overall_score' | 'gate' | 'est_tokens';

/** Sort direction */
type SortDirection = 'asc' | 'desc';

// ============================================
// Constants
// ============================================

/** Layer display names */
const LAYER_NAMES: Record<keyof LayerScores, string> = {
  L1_cost: 'L1 成本',
  L2_redundancy: 'L2 冗余',
  L3_safety: 'L3 安全',
  L4_structure: 'L4 结构',
  L5_evidence_ready: 'L5 证据',
};

/** API base for fetching audit reports */
const AUDIT_API_BASE = '/api/v1/audit';

// ============================================
// P1-2 Schema Validation
// ============================================

/** Validation error detail */
interface ValidationError {
  path: string;
  message: string;
}

/**
 * Validate audit report against schema
 * P1-2: 前端加载前校验，字段缺失必须显示可读错误
 *
 * @see schemas/skill_audit_report.schema.json
 */
function validateAuditReport(data: unknown): { valid: true; data: AuditReport } | { valid: false; errors: ValidationError[] } {
  const errors: ValidationError[] = [];

  // Must be an object
  if (typeof data !== 'object' || data === null) {
    return { valid: false, errors: [{ path: 'root', message: '数据必须是一个对象' }] };
  }

  const report = data as Record<string, unknown>;

  // Check required top-level fields
  if (!('summary' in report)) {
    errors.push({ path: 'summary', message: '缺少必需字段 summary' });
  }
  if (!('results' in report)) {
    errors.push({ path: 'results', message: '缺少必需字段 results' });
  }

  // Validate summary if present
  if ('summary' in report && typeof report.summary === 'object' && report.summary !== null) {
    const summary = report.summary as Record<string, unknown>;
    const summaryRequired = [
      'run_date', 'generated_at', 'profile', 'policy_version', 'policy_path',
      'scope', 'run_id', 'evidence_ref', 'input_hash', 'sample_size',
      'gate_counts', 'avg_overall_score', 'avg_est_tokens', 'result_hash'
    ];

    for (const field of summaryRequired) {
      if (!(field in summary)) {
        errors.push({ path: `summary.${field}`, message: `缺少必需字段 summary.${field}` });
      }
    }

    // Validate gate_counts
    if ('gate_counts' in summary && typeof summary.gate_counts === 'object' && summary.gate_counts !== null) {
      const gateCounts = summary.gate_counts as Record<string, unknown>;
      for (const key of ['PASS', 'WARN', 'FAIL']) {
        if (!(key in gateCounts)) {
          errors.push({ path: `summary.gate_counts.${key}`, message: `缺少必需字段 summary.gate_counts.${key}` });
        }
      }
    } else if ('gate_counts' in summary) {
      errors.push({ path: 'summary.gate_counts', message: 'gate_counts 必须是一个对象' });
    }
  }

  // Validate results if present
  if ('results' in report) {
    if (!Array.isArray(report.results)) {
      errors.push({ path: 'results', message: 'results 必须是一个数组' });
    } else {
      const resultRequired = [
        'domain', 'skill', 'path', 'source_sha256', 'evidence_ref',
        'chars', 'est_tokens', 'repeat_ratio', 'broken_links',
        'checklist_items', 'numbered_steps', 'tables', 'sensitive_hits',
        'has_disclaimer', 'has_review_warning', 'layer_scores',
        'layer_status', 'overall_score', 'gate'
      ];

      report.results.forEach((item, index) => {
        if (typeof item !== 'object' || item === null) {
          errors.push({ path: `results[${index}]`, message: `results[${index}] 必须是一个对象` });
          return;
        }

        const resultItem = item as Record<string, unknown>;
        for (const field of resultRequired) {
          if (!(field in resultItem)) {
            errors.push({ path: `results[${index}].${field}`, message: `缺少必需字段 results[${index}].${field}` });
          }
        }

        // Validate layer_scores
        if ('layer_scores' in resultItem && typeof resultItem.layer_scores === 'object' && resultItem.layer_scores !== null) {
          const layerScores = resultItem.layer_scores as Record<string, unknown>;
          for (const layer of ['L1_cost', 'L2_redundancy', 'L3_safety', 'L4_structure', 'L5_evidence_ready']) {
            if (!(layer in layerScores)) {
              errors.push({ path: `results[${index}].layer_scores.${layer}`, message: `缺少必需字段 results[${index}].layer_scores.${layer}` });
            }
          }
        }

        // Validate layer_status
        if ('layer_status' in resultItem && typeof resultItem.layer_status === 'object' && resultItem.layer_status !== null) {
          const layerStatus = resultItem.layer_status as Record<string, unknown>;
          for (const layer of ['L1_cost', 'L2_redundancy', 'L3_safety', 'L4_structure', 'L5_evidence_ready']) {
            if (!(layer in layerStatus)) {
              errors.push({ path: `results[${index}].layer_status.${layer}`, message: `缺少必需字段 results[${index}].layer_status.${layer}` });
            } else {
              const status = layerStatus[layer];
              if (status !== 'PASS' && status !== 'WARN' && status !== 'FAIL') {
                errors.push({ path: `results[${index}].layer_status.${layer}`, message: `layer_status.${layer} 必须是 PASS/WARN/FAIL 之一，实际为: ${status}` });
              }
            }
          }
        }

        // Validate gate
        if ('gate' in resultItem) {
          const gate = resultItem.gate;
          if (gate !== 'PASS' && gate !== 'WARN' && gate !== 'FAIL') {
            errors.push({ path: `results[${index}].gate`, message: `gate 必须是 PASS/WARN/FAIL 之一，实际为: ${gate}` });
          }
        }
      });
    }
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return { valid: true, data: data as AuditReport };
}

/**
 * Format validation errors into readable message
 * 约束: 字段缺失必须显示可读错误
 */
function formatValidationErrors(errors: ValidationError[]): string {
  if (errors.length === 0) return '未知校验错误';
  if (errors.length === 1) {
    return `数据格式错误: ${errors[0].path} - ${errors[0].message}`;
  }
  const details = errors.slice(0, 5).map(e => `${e.path}: ${e.message}`).join('; ');
  const more = errors.length > 5 ? ` (还有 ${errors.length - 5} 个错误)` : '';
  return `数据格式错误 (${errors.length} 项): ${details}${more}`;
}

// ============================================
// Sub-Components
// ============================================

/**
 * 总览卡组件 - Summary Card
 */
const SummaryCard: React.FC<{ summary: AuditSummary | null }> = ({ summary }) => {
  if (!summary) {
    return (
      <div style={styles.summaryCard}>
        <div style={styles.summaryEmpty}>暂无审计汇总数据</div>
      </div>
    );
  }

  return (
    <div style={styles.summaryCard}>
      <div style={styles.summaryHeader}>
        <h2 style={styles.summaryTitle}>📊 审计汇总</h2>
        <span style={styles.summaryRunId}>{summary.run_id}</span>
      </div>

      <div style={styles.summaryGrid}>
        {/* Left: Run Info */}
        <div style={styles.summarySection}>
          <div style={styles.summaryLabel}>运行日期</div>
          <div style={styles.summaryValue}>{summary.run_date}</div>
          <div style={styles.summaryLabel}>采样数量</div>
          <div style={styles.summaryValue}>{summary.sample_size}</div>
          <div style={styles.summaryLabel}>Profile</div>
          <div style={styles.summaryValueMono}>{summary.profile}</div>
        </div>

        {/* Center: Gate Counts */}
        <div style={styles.summarySection}>
          <div style={styles.summaryLabel}>Gate 结果</div>
          <div style={styles.gateCountRow}>
            <div style={styles.gateCountItem}>
              <span style={{ ...styles.gateCountBadge, backgroundColor: '#D1FAE5', color: '#059669' }}>
                {summary.gate_counts.PASS}
              </span>
              <span style={styles.gateCountLabel}>PASS</span>
            </div>
            <div style={styles.gateCountItem}>
              <span style={{ ...styles.gateCountBadge, backgroundColor: '#FEF3C7', color: '#D97706' }}>
                {summary.gate_counts.WARN}
              </span>
              <span style={styles.gateCountLabel}>WARN</span>
            </div>
            <div style={styles.gateCountItem}>
              <span style={{ ...styles.gateCountBadge, backgroundColor: '#FEE2E2', color: '#DC2626' }}>
                {summary.gate_counts.FAIL}
              </span>
              <span style={styles.gateCountLabel}>FAIL</span>
            </div>
          </div>
        </div>

        {/* Right: Scores */}
        <div style={styles.summarySection}>
          <div style={styles.summaryLabel}>平均分数</div>
          <div style={styles.scoreLarge}>{summary.avg_overall_score.toFixed(1)}</div>
          <div style={styles.summaryLabel}>平均 Token</div>
          <div style={styles.summaryValue}>{summary.avg_est_tokens.toFixed(0)}</div>
        </div>
      </div>

      <div style={styles.summaryMeta}>
        <span>Scope: {summary.scope}</span>
      </div>
    </div>
  );
};

/**
 * 状态徽章组件
 */
const GateBadge: React.FC<{ gate: 'PASS' | 'WARN' | 'FAIL' }> = ({ gate }) => {
  const config: Record<string, { bg: string; color: string }> = {
    PASS: { bg: '#D1FAE5', color: '#059669' },
    WARN: { bg: '#FEF3C7', color: '#D97706' },
    FAIL: { bg: '#FEE2E2', color: '#DC2626' },
  };

  const style = config[gate];

  return (
    <span style={{
      ...styles.badge,
      backgroundColor: style.bg,
      color: style.color,
    }}>
      {gate}
    </span>
  );
};

/**
 * 明细表组件 - Results Table
 */
const ResultsTable: React.FC<{
  results: AuditResultItem[];
  sortKey: SortKey;
  sortDirection: SortDirection;
  onSort: (key: SortKey) => void;
  onRowClick: (item: AuditResultItem) => void;
  selectedItem: AuditResultItem | null;
}> = ({ results, sortKey, sortDirection, onSort, onRowClick, selectedItem }) => {
  const getSortIndicator = (key: SortKey) => {
    if (sortKey !== key) return null;
    return sortDirection === 'asc' ? ' ▲' : ' ▼';
  };

  const thStyle = (_key: SortKey): React.CSSProperties => ({
    ...styles.thCell,
    cursor: 'pointer',
    userSelect: 'none',
  });

  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={thStyle('domain')} onClick={() => onSort('domain')}>
              Domain{getSortIndicator('domain')}
            </th>
            <th style={thStyle('skill')} onClick={() => onSort('skill')}>
              Skill{getSortIndicator('skill')}
            </th>
            <th style={thStyle('overall_score')} onClick={() => onSort('overall_score')}>
              Score{getSortIndicator('overall_score')}
            </th>
            <th style={thStyle('gate')} onClick={() => onSort('gate')}>
              Gate{getSortIndicator('gate')}
            </th>
            <th style={thStyle('est_tokens')} onClick={() => onSort('est_tokens')}>
              Tokens{getSortIndicator('est_tokens')}
            </th>
            <th>L1</th>
            <th>L2</th>
            <th>L3</th>
            <th>L4</th>
            <th>L5</th>
          </tr>
        </thead>
        <tbody>
          {results.map((item, index) => (
            <tr
              key={`${item.domain}-${item.skill}-${index}`}
              style={{
                ...styles.tableRow,
                backgroundColor: selectedItem === item ? '#EFF6FF' : '#FFFFFF',
              }}
              onClick={() => onRowClick(item)}
            >
              <td style={styles.tableCell}>{item.domain}</td>
              <td style={styles.tableCell}>{item.skill}</td>
              <td style={styles.tableCellScore}>
                <span style={{
                  color: item.overall_score >= 80 ? '#059669' :
                         item.overall_score >= 60 ? '#D97706' : '#DC2626',
                  fontWeight: 600,
                }}>
                  {item.overall_score.toFixed(0)}
                </span>
              </td>
              <td style={styles.tableCell}><GateBadge gate={item.gate} /></td>
              <td style={styles.tableCellMono}>{item.est_tokens}</td>
              <td style={styles.tableCellLayer}>
                <LayerMiniStatus status={item.layer_status.L1_cost} score={item.layer_scores.L1_cost} />
              </td>
              <td style={styles.tableCellLayer}>
                <LayerMiniStatus status={item.layer_status.L2_redundancy} score={item.layer_scores.L2_redundancy} />
              </td>
              <td style={styles.tableCellLayer}>
                <LayerMiniStatus status={item.layer_status.L3_safety} score={item.layer_scores.L3_safety} />
              </td>
              <td style={styles.tableCellLayer}>
                <LayerMiniStatus status={item.layer_status.L4_structure} score={item.layer_scores.L4_structure} />
              </td>
              <td style={styles.tableCellLayer}>
                <LayerMiniStatus status={item.layer_status.L5_evidence_ready} score={item.layer_scores.L5_evidence_ready} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/**
 * 层级迷你状态组件
 */
const LayerMiniStatus: React.FC<{ status: LayerStatus; score: number }> = ({ status, score }) => {
  const color = status === 'PASS' ? '#059669' : status === 'WARN' ? '#D97706' : '#DC2626';

  return (
    <span style={{ color, fontSize: '12px', fontWeight: 500 }}>
      {score}
    </span>
  );
};

/**
 * 详情面板组件
 */
const DetailPanel: React.FC<{
  item: AuditResultItem | null;
  onClose: () => void;
}> = ({ item, onClose }) => {
  if (!item) {
    return (
      <div style={styles.detailPanel}>
        <div style={styles.detailEmpty}>
          <span style={styles.detailEmptyIcon}>🔍</span>
          <span>选择表格行查看详情</span>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.detailPanel}>
      <div style={styles.detailHeader}>
        <h3 style={styles.detailTitle}>{item.domain} / {item.skill}</h3>
        <button onClick={onClose} style={styles.closeButton}>✕</button>
      </div>

      <div style={styles.detailContent}>
        {/* Gate Result */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>Gate 结果</div>
          <div style={styles.gateResultRow}>
            <GateBadge gate={item.gate} />
            <span style={styles.overallScore}>Overall: {item.overall_score.toFixed(0)}</span>
          </div>
        </div>

        {/* Layer Scores */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>L1-L5 层级分数</div>
          {(Object.keys(item.layer_scores) as (keyof LayerScores)[]).map((layer) => (
            <div key={layer} style={styles.layerRow}>
              <span style={styles.layerName}>{LAYER_NAMES[layer]}</span>
              <div style={styles.scoreBar}>
                <div
                  style={{
                    ...styles.scoreBarFill,
                    width: `${item.layer_scores[layer]}%`,
                    backgroundColor: item.layer_status[layer] === 'PASS' ? '#10B981' :
                                     item.layer_status[layer] === 'WARN' ? '#F59E0B' : '#EF4444',
                  }}
                />
              </div>
              <span style={styles.layerScore}>{item.layer_scores[layer]}</span>
              <GateBadge gate={item.layer_status[layer]} />
            </div>
          ))}
        </div>

        {/* Metrics */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>指标</div>
          <div style={styles.metricGrid}>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>字符数</span>
              <span style={styles.metricValue}>{item.chars.toLocaleString()}</span>
            </div>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>估算 Token</span>
              <span style={styles.metricValue}>{item.est_tokens.toLocaleString()}</span>
            </div>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>重复率</span>
              <span style={styles.metricValue}>{(item.repeat_ratio * 100).toFixed(1)}%</span>
            </div>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>步骤数</span>
              <span style={styles.metricValue}>{item.numbered_steps}</span>
            </div>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>表格数</span>
              <span style={styles.metricValue}>{item.tables}</span>
            </div>
            <div style={styles.metricItem}>
              <span style={styles.metricLabel}>检查项</span>
              <span style={styles.metricValue}>{item.checklist_items}</span>
            </div>
          </div>
        </div>

        {/* Evidence */}
        <div style={styles.detailSection}>
          <div style={styles.sectionTitle}>Evidence Ref</div>
          <code style={styles.evidenceCode}>{item.evidence_ref}</code>
        </div>
      </div>
    </div>
  );
};

/**
 * 结论限制区组件 - Limitations Panel
 */
const LimitationsPanel: React.FC<{ summary: AuditSummary | null }> = ({ summary }) => {
  if (!summary) return null;

  return (
    <div style={styles.limitationsPanel}>
      <div style={styles.limitationsHeader}>
        <span style={styles.limitationsIcon}>⚠️</span>
        <span style={styles.limitationsTitle}>结论与限制</span>
      </div>
      <div style={styles.limitationsContent}>
        <div style={styles.limitationItem}>
          <span style={styles.limitationLabel}>Policy Version:</span>
          <span style={styles.limitationValue}>{summary.policy_version}</span>
        </div>
        <div style={styles.limitationItem}>
          <span style={styles.limitationLabel}>Policy Path:</span>
          <code style={styles.limitationCode}>{summary.policy_path}</code>
        </div>
        <div style={styles.limitationItem}>
          <span style={styles.limitationLabel}>Evidence Ref:</span>
          <code style={styles.limitationCode}>{summary.evidence_ref}</code>
        </div>
        <div style={styles.limitationItem}>
          <span style={styles.limitationLabel}>Result Hash:</span>
          <code style={styles.limitationCodeSmall}>{summary.result_hash.slice(0, 16)}...</code>
        </div>
        <div style={styles.limitationsNote}>
          <strong>限制说明:</strong> 本审计结果仅针对指定 scope 内的技能样本，
          不代表全量技能审计。结论基于当前 policy 版本，后续 policy 变更可能导致结果差异。
        </div>
      </div>
    </div>
  );
};

// ============================================
// Main Component
// ============================================

export const SkillAuditPage: React.FC = () => {
  // State
  const [report, setReport] = useState<AuditReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>('overall_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedItem, setSelectedItem] = useState<AuditResultItem | null>(null);

  // Fetch audit report
  useEffect(() => {
    const fetchReport = async () => {
      setIsLoading(true);
      setError(null);

      try {
        let rawData: unknown;

        // 尝试从 API 获取最新报告
        const response = await fetch(`${AUDIT_API_BASE}/skill-audit/latest`);
        if (response.ok) {
          rawData = await response.json();
        } else {
          // API 不可用，尝试从静态资源加载
          // 这里使用真实的 JSON 文件路径（public 目录映射）
          const staticResponse = await fetch('/reports/skill-audit/finance_legal_top3_l5-static_2026-02-22.json');
          if (staticResponse.ok) {
            rawData = await staticResponse.json();
          } else {
            throw new Error('无法加载审计报告');
          }
        }

        // P1-2: 加载前进行 Schema 校验
        // 约束: 字段缺失必须显示可读错误，不得静默吞掉校验失败
        const validationResult = validateAuditReport(rawData);
        if (validationResult.valid) {
          setReport(validationResult.data);
        } else {
          // validationResult is narrowed to { valid: false; errors: ValidationError[] }
          const errorMsg = formatValidationErrors(validationResult.errors);
          console.error('[SkillAuditPage] Schema validation failed:', validationResult.errors);
          throw new Error(errorMsg);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '加载审计报告失败');
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, []);

  // Sort results
  const sortedResults = useMemo(() => {
    if (!report?.results) return [];

    const sorted = [...report.results].sort((a, b) => {
      let cmp = 0;

      switch (sortKey) {
        case 'domain':
          cmp = a.domain.localeCompare(b.domain);
          break;
        case 'skill':
          cmp = a.skill.localeCompare(b.skill);
          break;
        case 'overall_score':
          cmp = a.overall_score - b.overall_score;
          break;
        case 'gate':
          const gateOrder = { PASS: 0, WARN: 1, FAIL: 2 };
          cmp = gateOrder[a.gate] - gateOrder[b.gate];
          break;
        case 'est_tokens':
          cmp = a.est_tokens - b.est_tokens;
          break;
      }

      return sortDirection === 'asc' ? cmp : -cmp;
    });

    return sorted;
  }, [report?.results, sortKey, sortDirection]);

  // Handle sort
  const handleSort = useCallback((key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  }, [sortKey]);

  // Handle row click
  const handleRowClick = useCallback((item: AuditResultItem) => {
    setSelectedItem(prev => prev === item ? null : item);
  }, []);

  // Render
  if (isLoading) {
    return (
      <div style={styles.page}>
        <div style={styles.loading}>
          <div style={styles.spinner}>⏳</div>
          <span>加载审计报告中...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.error}>
          <span style={styles.errorIcon}>❌</span>
          <span>加载失败: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      {/* Page Header */}
      <header style={styles.pageHeader}>
        <h1 style={styles.pageTitle}>🔍 技能审计结果</h1>
        <div style={styles.pageSubtitle}>P1-1 审计结果页 | Skill Audit Report</div>
      </header>

      {/* Main Content */}
      <div style={styles.mainContent}>
        {/* Left: Summary + Table */}
        <div style={styles.leftPanel}>
          {/* Summary Card */}
          <SummaryCard summary={report?.summary ?? null} />

          {/* Results Table */}
          <div style={styles.tableSection}>
            <div style={styles.tableHeader}>
              <span>审计明细 ({sortedResults.length} 项)</span>
              <span style={styles.sortHint}>点击列头排序</span>
            </div>
            <ResultsTable
              results={sortedResults}
              sortKey={sortKey}
              sortDirection={sortDirection}
              onSort={handleSort}
              onRowClick={handleRowClick}
              selectedItem={selectedItem}
            />
          </div>

          {/* Limitations */}
          <LimitationsPanel summary={report?.summary ?? null} />
        </div>

        {/* Right: Detail Panel */}
        <DetailPanel item={selectedItem} onClose={() => setSelectedItem(null)} />
      </div>
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
    overflow: 'hidden',
  },
  pageHeader: {
    padding: '16px 24px',
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E5E7EB',
    flexShrink: 0,
  },
  pageTitle: {
    fontSize: '22px',
    fontWeight: 600,
    color: '#1F2937',
    margin: 0,
  },
  pageSubtitle: {
    fontSize: '13px',
    color: '#6B7280',
    marginTop: '4px',
  },
  mainContent: {
    display: 'flex',
    flex: 1,
    minHeight: 0,
    overflow: 'hidden',
  },
  leftPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    minWidth: 0,
    overflow: 'auto',
    padding: '16px',
    gap: '16px',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#6B7280',
    gap: '12px',
  },
  spinner: {
    fontSize: '32px',
  },
  error: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#DC2626',
    gap: '12px',
  },
  errorIcon: {
    fontSize: '32px',
  },

  // Summary Card
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #E5E7EB',
  },
  summaryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  summaryTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1F2937',
    margin: 0,
  },
  summaryRunId: {
    fontSize: '11px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#6B7280',
  },
  summaryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
  },
  summarySection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  summaryLabel: {
    fontSize: '11px',
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  summaryValue: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#1F2937',
  },
  summaryValueMono: {
    fontSize: '13px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#1F2937',
  },
  scoreLarge: {
    fontSize: '28px',
    fontWeight: 700,
    color: '#3B82F6',
  },
  gateCountRow: {
    display: 'flex',
    gap: '12px',
    marginTop: '8px',
  },
  gateCountItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  },
  gateCountBadge: {
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 600,
  },
  gateCountLabel: {
    fontSize: '10px',
    color: '#6B7280',
  },
  summaryEmpty: {
    padding: '24px',
    textAlign: 'center',
    color: '#9CA3AF',
  },
  summaryMeta: {
    marginTop: '12px',
    fontSize: '11px',
    color: '#6B7280',
    paddingTop: '12px',
    borderTop: '1px solid #E5E7EB',
  },

  // Table
  tableSection: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    borderRadius: '8px',
    border: '1px solid #E5E7EB',
    minHeight: 0,
    overflow: 'hidden',
  },
  tableHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid #E5E7EB',
    fontSize: '13px',
    fontWeight: 600,
    color: '#374151',
  },
  sortHint: {
    fontSize: '11px',
    fontWeight: 400,
    color: '#9CA3AF',
  },
  tableContainer: {
    flex: 1,
    overflow: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '13px',
  },
  thCell: {
    padding: '10px 12px',
    textAlign: 'left',
    borderBottom: '2px solid #E5E7EB',
    fontWeight: 600,
    color: '#374151',
    backgroundColor: '#F9FAFB',
    position: 'sticky',
    top: 0,
  },
  tableRow: {
    cursor: 'pointer',
    transition: 'background-color 0.15s',
    borderBottom: '1px solid #E5E7EB',
  },
  tableCell: {
    padding: '10px 12px',
    color: '#1F2937',
  },
  tableCellScore: {
    padding: '10px 12px',
    textAlign: 'center',
  },
  tableCellMono: {
    padding: '10px 12px',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '12px',
  },
  tableCellLayer: {
    padding: '10px 8px',
    textAlign: 'center',
  },
  badge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 600,
  },

  // Detail Panel
  detailPanel: {
    width: '360px',
    flexShrink: 0,
    backgroundColor: '#FFFFFF',
    borderLeft: '1px solid #E5E7EB',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
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
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    borderBottom: '1px solid #E5E7EB',
  },
  detailTitle: {
    fontSize: '15px',
    fontWeight: 600,
    color: '#1F2937',
    margin: 0,
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    color: '#6B7280',
    cursor: 'pointer',
  },
  detailContent: {
    flex: 1,
    overflow: 'auto',
    padding: '16px',
  },
  detailSection: {
    marginBottom: '20px',
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
  gateResultRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  overallScore: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  layerRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px',
  },
  layerName: {
    width: '80px',
    fontSize: '12px',
    color: '#6B7280',
  },
  scoreBar: {
    flex: 1,
    height: '8px',
    backgroundColor: '#E5E7EB',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  scoreBarFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.3s',
  },
  layerScore: {
    width: '32px',
    fontSize: '12px',
    fontWeight: 600,
    textAlign: 'right',
  },
  metricGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
  },
  metricItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  },
  metricLabel: {
    fontSize: '10px',
    color: '#6B7280',
  },
  metricValue: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1F2937',
  },
  evidenceCode: {
    fontSize: '11px',
    fontFamily: "'JetBrains Mono', monospace",
    color: '#3B82F6',
    wordBreak: 'break-all',
    backgroundColor: '#EFF6FF',
    padding: '8px 12px',
    borderRadius: '4px',
    display: 'block',
  },

  // Limitations Panel
  limitationsPanel: {
    backgroundColor: '#FFFBEB',
    borderRadius: '8px',
    border: '1px solid #FCD34D',
    padding: '16px',
  },
  limitationsHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
  },
  limitationsIcon: {
    fontSize: '18px',
  },
  limitationsTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#92400E',
  },
  limitationsContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  limitationItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
  },
  limitationLabel: {
    color: '#92400E',
    fontWeight: 500,
  },
  limitationValue: {
    color: '#78350F',
  },
  limitationCode: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '11px',
    color: '#78350F',
    backgroundColor: 'rgba(252, 211, 77, 0.3)',
    padding: '2px 6px',
    borderRadius: '3px',
  },
  limitationCodeSmall: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '10px',
    color: '#78350F',
  },
  limitationsNote: {
    marginTop: '8px',
    fontSize: '11px',
    color: '#92400E',
    lineHeight: 1.5,
  },
};

export default SkillAuditPage;
