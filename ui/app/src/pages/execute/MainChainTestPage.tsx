/**
 * MainChainTestPage
 *
 * 主链状态测试页面 - 展示如何使用 MainChainStatusPanel 组件
 *
 * 用途: TASK-MAIN-04B - 测试前端承接真实 RunResult 和 ArtifactManifest
 *
 * 本页面演示:
 * - 从真实 JSON 文件加载 RunResult
 * - 从真实 JSON 文件加载 ArtifactManifest
 * - 使用 MainChainStatusPanel 展示完整主链状态
 * - 提供证据入口交互
 */

import React, { useState, useEffect, useCallback } from 'react';
import { MainChainStatusPanel } from '../../components/governance/MainChainStatusPanel';
import type { RunResult } from '../../types/runtimeInterface';
import { mapToRunResult } from '../../mappers/runtimeInterfaceMapper';
import styles from './MainChainTestPage.module.css';

// 测试数据路径 (相对于 docs/ 根目录)
const TEST_RUN_RESULT_PATH = '/docs/2026-03-11/REAL-TASK-002/run_result.json';
const TEST_MANIFEST_PATH = '/docs/2026-03-11/REAL-TASK-002/artifact_manifest.json';

export const MainChainTestPage: React.FC = () => {
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDataSource, setSelectedDataSource] = useState<'real' | 'mock'>('real');

  // 加载真实数据
  const loadRealData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // 加载 RunResult
      const runResultResponse = await fetch(TEST_RUN_RESULT_PATH);
      if (!runResultResponse.ok) {
        throw new Error(`Failed to load RunResult: ${runResultResponse.statusText}`);
      }
      const runResultData = await runResultResponse.json();
      const mappedRunResult = mapToRunResult(runResultData);

      setRunResult(mappedRunResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      console.error('Failed to load real data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 加载模拟数据
  const loadMockData = useCallback(() => {
    setLoading(true);
    setError(null);

    const mockRunResult: RunResult = {
      schema_version: 'runtime_interface_v0.1',
      task_id: 'MOCK-TASK-001',
      run_id: 'MOCK-RUN-001',
      executor: 'test_executor',
      status: 'success',
      started_at: new Date(Date.now() - 10000).toISOString(),
      finished_at: new Date().toISOString(),
      executed_commands: ['echo "test"'],
      exit_code: 0,
      output: { test: 'data' },
      summary: '模拟执行成功 - 用于测试前端展示',
      evidence_refs: [
        {
          issue_key: 'MOCK-001',
          source_locator: '/mock/evidence/test.md',
          content_hash: 'sha256:mockhash',
          tool_revision: 'test_v1',
          timestamp: new Date().toISOString(),
          kind: 'FILE',
        },
      ],
      manifest: {
        schema_version: 'runtime_interface_v0.1',
        task_id: 'MOCK-TASK-001',
        run_id: 'MOCK-RUN-001',
        artifacts: [
          {
            path: 'mock/blueprint.md',
            kind: 'blueprint',
            content_hash: 'sha256:mock',
            size_bytes: 1024,
          },
        ],
        evidence: [
          {
            path: 'mock/evidence/test.md',
            kind: 'evidence',
            content_hash: 'sha256:mock',
            size_bytes: 512,
          },
        ],
        env: {},
        created_at: new Date().toISOString(),
      },
    };

    setRunResult(mockRunResult);
    setLoading(false);
    setSelectedDataSource('mock');
  }, []);

  // 初始加载
  useEffect(() => {
    if (selectedDataSource === 'real') {
      loadRealData();
    } else {
      loadMockData();
    }
  }, [selectedDataSource, loadRealData, loadMockData]);

  // 处理重新加载
  const handleReload = () => {
    if (selectedDataSource === 'real') {
      loadRealData();
    } else {
      loadMockData();
    }
  };

  // 处理数据源切换
  const handleDataSourceChange = (source: 'real' | 'mock') => {
    setSelectedDataSource(source);
  };

  return (
    <div className={styles.container}>
      {/* 页面头部 */}
      <div className={styles.header}>
        <h1 className={styles.title}>主链状态测试页面</h1>
        <p className={styles.description}>
          TASK-MAIN-04B: 前端承接主链状态、证据入口和运行结果
        </p>
      </div>

      {/* 控制面板 */}
      <div className={styles.controlPanel}>
        <div className={styles.dataSourceSection}>
          <span className={styles.dataSourceLabel}>数据源:</span>
          <button
            className={`${styles.dataSourceButton} ${selectedDataSource === 'real' ? styles.active : ''}`}
            onClick={() => handleDataSourceChange('real')}
          >
            真实数据 (REAL-TASK-002)
          </button>
          <button
            className={`${styles.dataSourceButton} ${selectedDataSource === 'mock' ? styles.active : ''}`}
            onClick={() => handleDataSourceChange('mock')}
          >
            模拟数据
          </button>
        </div>

        <button className={styles.reloadButton} onClick={handleReload}>
          🔄 重新加载
        </button>
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <span>加载中...</span>
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <div className={styles.errorState}>
          <h3>⚠️ 加载失败</h3>
          <p>{error}</p>
          <p className={styles.errorHint}>
            提示: 确保文件存在于 <code>{TEST_RUN_RESULT_PATH}</code>
          </p>
          <button className={styles.retryButton} onClick={handleReload}>
            重试
          </button>
        </div>
      )}

      {/* 主链状态面板 */}
      {!loading && !error && runResult && (
        <div className={styles.content}>
          <div className={styles.panelSection}>
            <h2 className={styles.sectionTitle}>完整主链状态展示</h2>
            <MainChainStatusPanel
              runResult={runResult}
              showDetails={true}
            />
          </div>

          {/* 调试信息 */}
          <details className={styles.debugSection}>
            <summary>调试信息 (原始 JSON)</summary>
            <pre className={styles.jsonPreview}>
              {JSON.stringify(runResult, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {/* 使用说明 */}
      <div className={styles.usageSection}>
        <h2 className={styles.sectionTitle}>使用说明</h2>
        <div className={styles.usageContent}>
          <h3>真实数据路径:</h3>
          <ul className={styles.usageList}>
            <li>
              <code>RunResult: {TEST_RUN_RESULT_PATH}</code>
            </li>
            <li>
              <code>ArtifactManifest: {TEST_MANIFEST_PATH}</code>
            </li>
          </ul>

          <h3>组件用法:</h3>
          <pre className={styles.codeExample}>
{`import { MainChainStatusPanel } from './components/governance/MainChainStatusPanel';
import type { RunResult } from './types/runtimeInterface';

// 在你的组件中
<MainChainStatusPanel
  runResult={runResult}
  showDetails={true}
  stepOrder={['permit', 'pre_absorb_check', 'absorb', 'local_accept', 'final_accept']}
/>`}
          </pre>

          <h3>数据映射:</h3>
          <pre className={styles.codeExample}>
{`import { mapToRunResult } from './mappers/runtimeInterfaceMapper';

// 从 API 或 JSON 文件加载数据后
const runResult = mapToRunResult(jsonData);`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default MainChainTestPage;
