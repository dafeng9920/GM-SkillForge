/**
 * Application Router Configuration
 *
 * v1.0 五页路由：
 * - /execute/run-intent    执行意图
 * - /execute/import-skill  外部技能导入
 * - /audit/packs           AuditPack 浏览
 * - /audit/rag-query       RAG 查询
 * - /system/health         健康监控
 *
 * 设计规范：
 * - 不出现 n8n 顶层一级导航
 * - 按业务域分组（execute/audit/system）
 *
 * @module app/router
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md
 */

import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

import { AppShell } from './layout/AppShell';

// Pages
import { RunIntentPage } from '../pages/execute/RunIntentPage';
import { ImportSkillPage } from '../pages/execute/ImportSkillPage';
import { AuditPacksPage } from '../pages/audit/AuditPacksPage';

// Placeholder pages - to be implemented by other tasks
const RagQueryPage = React.lazy(() => import('../pages/audit/RagQueryPage'));
const HealthPage = React.lazy(() => import('../pages/system/HealthPage'));
const SkillAuditPage = React.lazy(() => import('../pages/audit/SkillAuditPage'));

/**
 * Simple loading component for lazy-loaded pages
 */
const PageLoader: React.FC = () => (
  <div style={loaderStyles}>
    <div style={spinnerStyles}>
      <svg
        width="40"
        height="40"
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          cx="20"
          cy="20"
          r="18"
          stroke="#E5E7EB"
          strokeWidth="3"
        />
        <path
          d="M38 20C38 30.4934 29.4934 39 19 39"
          stroke="#1890FF"
          strokeWidth="3"
          strokeLinecap="round"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 20 20"
            to="360 20 20"
            dur="1s"
            repeatCount="indefinite"
          />
        </path>
      </svg>
    </div>
    <span style={{ color: '#6B7280', fontSize: '14px' }}>加载中...</span>
  </div>
);

const loaderStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  height: '100%',
  minHeight: '400px',
  gap: '16px',
};

const spinnerStyles: React.CSSProperties = {
  animation: 'spin 1s linear infinite',
};

/**
 * Route configuration for v1.0
 *
 * Structure:
 * /                        → Redirect to /execute/run-intent
 * /execute/run-intent      → Run Intent page
 * /execute/import-skill    → Import Skill page
 * /audit/packs             → Audit Packs page
 * /audit/rag-query         → RAG Query page
 * /audit/skill-audit       → Skill Audit page (P1-1)
 * /system/health           → Health page
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      // Default redirect to Run Intent (primary action)
      {
        index: true,
        element: <Navigate to="/execute/run-intent" replace />,
      },

      // Execute group
      {
        path: 'execute',
        children: [
          {
            path: 'run-intent',
            element: <RunIntentPage />,
          },
          {
            path: 'import-skill',
            element: <ImportSkillPage />,
          },
        ],
      },

      // Audit group
      {
        path: 'audit',
        children: [
          {
            path: 'packs',
            element: <AuditPacksPage />,
          },
          {
            path: 'rag-query',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <RagQueryPage />
              </React.Suspense>
            ),
          },
          {
            path: 'skill-audit',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <SkillAuditPage />
              </React.Suspense>
            ),
          },
        ],
      },

      // System group
      {
        path: 'system',
        children: [
          {
            path: 'health',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <HealthPage />
              </React.Suspense>
            ),
          },
        ],
      },

      // Catch-all: redirect unknown routes to home
      {
        path: '*',
        element: <Navigate to="/execute/run-intent" replace />,
      },
    ],
  },
]);

export default router;
