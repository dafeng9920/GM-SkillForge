/**
 * Application Router Configuration
 *
 * v2.0 治理主链路由：
 * - /home                   极简 AI 首页（默认首页）
 * - /dashboard              治理总控台
 * - /intake/vetting         外部 Skill Vetting 入口
 * - /intake/vetting/report  Vetting 报告
 * - /registry               资产登记
 * - /audit/detail           审计详情
 * - /permit                 放行凭证
 * - /release/vetting-permit Vetting Permit 决策页
 * - /forge                  构建（次级入口）
 * - /policies               策略配置
 * - /history                历史记录
 *
 * 设计规范：
 * - 治理主链：Dashboard / Audit Detail / Permit
 * - 次级导航：Registry / Forge / Policies / History
 * - 禁止 builder-first 一级导航
 * - 首页讲价值，应用内讲状态、裁决、证据与放行
 *
 * @module app/router
 * @see docs/2026-03-12/verification/T-FE-01_ia_spec.md
 * @see docs/2026-03-12/verification/T-FE-07_copy_and_cta_spec.md
 */

import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

import { AppShell } from './layout/AppShell';

const HomePage = React.lazy(() => import('../pages/governance/HomePage'));
const DashboardPage = React.lazy(() => import('../pages/governance/DashboardPage'));
const VettingHomePage = React.lazy(() => import('../pages/governance/VettingHomePage'));
const VettingReportPage = React.lazy(() => import('../pages/governance/VettingReportPage'));
const VettingPermitDecisionPage = React.lazy(() => import('../pages/governance/VettingPermitDecisionPage'));
const RegistryPage = React.lazy(() => import('../pages/governance/RegistryPage'));
const AuditDetailPage = React.lazy(() => import('../pages/governance/AuditDetailPage'));
const PermitPage = React.lazy(() => import('../pages/governance/PermitPage'));
const ForgePage = React.lazy(() => import('../pages/governance/ForgePage'));
const PoliciesPage = React.lazy(() => import('../pages/governance/PoliciesPage'));
const HistoryPage = React.lazy(() => import('../pages/governance/HistoryPage'));

// Legacy pages - maintained for backward compatibility, not promoted to main navigation
const RunIntentPage = React.lazy(() => import('../pages/execute/RunIntentPage'));
const ImportSkillPage = React.lazy(() => import('../pages/execute/ImportSkillPage'));
const AuditPacksPage = React.lazy(() => import('../pages/audit/AuditPacksPage'));
const RagQueryPage = React.lazy(() => import('../pages/audit/RagQueryPage'));
const HealthPage = React.lazy(() => import('../pages/system/HealthPage'));

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
 * Route configuration for v2.0 (Governance-First)
 *
 * Structure:
 * /                        → Redirect to /home
 * /home                    → Minimal AI-style homepage
 * /dashboard               → Dashboard page (治理总控台)
 * /intake/vetting          → Vetting intake gate page
 * /intake/vetting/report   → Vetting report page
 * /registry                → Registry page (资产登记 - P2)
 * /audit/detail            → Audit Detail page (审计详情 - P0)
 * /permit                  → Permit page (放行凭证 - P0)
 * /release/vetting-permit  → Vetting permit decision page
 * /forge                   → Forge page (构建 - 次级入口)
 * /policies                → Policies page (策略配置 - P3)
 * /history                 → History page (历史记录 - P3)
 *
 * Legacy routes (maintained for backward compatibility):
 * /execute/*               → Legacy execute pages
 * /audit/packs             → Legacy Audit Packs page
 * /audit/rag-query         → Legacy RAG Query page
 * /system/health           → Legacy Health page
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      // Default redirect to Home
      {
        index: true,
        element: <Navigate to="/home" replace />,
      },

      {
        path: 'home',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <HomePage />
          </React.Suspense>
        ),
      },

      // === Main Chain: Dashboard / Audit Detail / Permit ===

      // Dashboard - 治理总控台 (P1)
      {
        path: 'dashboard',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <DashboardPage />
          </React.Suspense>
        ),
      },

      {
        path: 'intake/vetting',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <VettingHomePage />
          </React.Suspense>
        ),
      },
      {
        path: 'intake/vetting/report',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <VettingReportPage />
          </React.Suspense>
        ),
      },

      // Audit Detail - 审计详情 (P0)
      {
        path: 'audit/detail',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <AuditDetailPage />
          </React.Suspense>
        ),
      },

      // Permit - 放行凭证 (P0)
      {
        path: 'permit',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <PermitPage />
          </React.Suspense>
        ),
      },
      {
        path: 'release/vetting-permit',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <VettingPermitDecisionPage />
          </React.Suspense>
        ),
      },

      // === Secondary Navigation: Registry / Forge / Policies / History ===

      // Registry - 资产登记 (P2)
      {
        path: 'registry',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <RegistryPage />
          </React.Suspense>
        ),
      },

      // Forge - 构建 (次级入口, P4)
      {
        path: 'forge',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <ForgePage />
          </React.Suspense>
        ),
      },

      // Policies - 策略配置 (P3)
      {
        path: 'policies',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <PoliciesPage />
          </React.Suspense>
        ),
      },

      // History - 历史记录 (P3)
      {
        path: 'history',
        element: (
          <React.Suspense fallback={<PageLoader />}>
            <HistoryPage />
          </React.Suspense>
        ),
      },

      // === Legacy Routes (maintained for backward compatibility, not in main navigation) ===

      // Legacy execute routes
      {
        path: 'execute',
        children: [
          {
            path: 'run-intent',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <RunIntentPage />
              </React.Suspense>
            ),
          },
          {
            path: 'import-skill',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <ImportSkillPage />
              </React.Suspense>
            ),
          },
        ],
      },

      // Legacy audit routes
      {
        path: 'audit',
        children: [
          {
            path: 'packs',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <AuditPacksPage />
              </React.Suspense>
            ),
          },
          {
            path: 'rag-query',
            element: (
              <React.Suspense fallback={<PageLoader />}>
                <RagQueryPage />
              </React.Suspense>
            ),
          },
        ],
      },

      // Legacy system routes
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

      // Catch-all: redirect unknown routes to Home
      {
        path: '*',
        element: <Navigate to="/home" replace />,
      },
    ],
  },
]);

export default router;
