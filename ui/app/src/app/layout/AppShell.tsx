/**
 * App Shell - 统一导航框架
 *
 * 功能：
 * - 一级导航 3 组（执行/审计/系统）
 * - Top Bar 预留 run_id 全局检索入口
 * - 响应式布局
 *
 * 设计规范：
 * - 不出现 n8n 顶层一级导航
 * - 工业控制台风格（白底高对比）
 * - 审计中台风格
 *
 * @module app/layout/AppShell
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md
 */

import React, { useState, useCallback } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

// ============================================
// Types
// ============================================

interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  children?: NavItem[];
}

// ============================================
// Constants
// ============================================

const NAV_GROUPS: { group: string; items: NavItem[] }[] = [
  {
    group: '执行中心',
    items: [
      { id: 'run-intent', label: '执行意图', path: '/execute/run-intent', icon: '▶' },
      { id: 'import-skill', label: '技能导入', path: '/execute/import-skill', icon: '📦' },
    ],
  },
  {
    group: '审计与查询',
    items: [
      { id: 'packs', label: '审计包', path: '/audit/packs', icon: '📋' },
      { id: 'rag-query', label: 'RAG 查询', path: '/audit/rag-query', icon: '🔍' },
    ],
  },
  {
    group: '系统运维',
    items: [
      { id: 'health', label: '健康监控', path: '/system/health', icon: '💚' },
    ],
  },
];

const STATUS_COLORS = {
  primary: '#1890FF',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  gray: '#6B7280',
};

// ============================================
// Sub-Components
// ============================================

const GlobalSearch: React.FC<{
  value: string;
  onChange: (value: string) => void;
  onSearch: (value: string) => void;
}> = ({ value, onChange, onSearch }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && value.trim()) {
      onSearch(value.trim());
    }
  };

  return (
    <div style={searchContainerStyles}>
      <span style={searchIconStyles}>🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="搜索 run_id 或 evidence_ref..."
        style={searchInputStyles}
      />
      {value && (
        <button
          onClick={() => onChange('')}
          style={searchClearStyles}
          title="清除"
        >
          ✕
        </button>
      )}
    </div>
  );
};

const NavLink: React.FC<{
  item: NavItem;
  isActive: boolean;
  onClick: () => void;
}> = ({ item, isActive, onClick }) => (
  <button
    onClick={onClick}
    style={{
      ...navLinkStyles,
      ...(isActive ? activeNavLinkStyles : {}),
    }}
    title={item.label}
  >
    <span style={navIconStyles}>{item.icon}</span>
    <span style={navLabelStyles}>{item.label}</span>
  </button>
);

const NavGroup: React.FC<{
  group: string;
  items: NavItem[];
  activePath: string;
  onNavigate: (path: string) => void;
}> = ({ group, items, activePath, onNavigate }) => (
  <div style={navGroupStyles}>
    <div style={navGroupTitleStyles}>{group}</div>
    {items.map((item) => (
      <NavLink
        key={item.id}
        item={item}
        isActive={activePath === item.path}
        onClick={() => onNavigate(item.path)}
      />
    ))}
  </div>
);

// ============================================
// Main Component
// ============================================

export const AppShell: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchValue, setSearchValue] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleNavigate = useCallback((path: string) => {
    navigate(path);
  }, [navigate]);

  const handleSearch = useCallback((query: string) => {
    // TODO: Implement global search - navigate to audit packs with search query
    // For now, just navigate to audit packs page
    navigate(`/audit/packs?search=${encodeURIComponent(query)}`);
  }, [navigate]);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  return (
    <div style={shellStyles}>
      {/* Top Bar */}
      <header style={topBarStyles}>
        <div style={topBarLeftStyles}>
          <button
            onClick={toggleSidebar}
            style={menuButtonStyles}
            title={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
          >
            ☰
          </button>
          <div style={logoStyles}>
            <span style={logoIconStyles}>⚡</span>
            <span style={logoTextStyles}>SkillForge</span>
            <span style={versionBadgeStyles}>v1.0</span>
          </div>
        </div>

        {/* Global Search - run_id / evidence_ref */}
        <div style={searchWrapperStyles}>
          <GlobalSearch
            value={searchValue}
            onChange={setSearchValue}
            onSearch={handleSearch}
          />
        </div>

        <div style={topBarRightStyles}>
          {/* Status indicator placeholder */}
          <div style={statusIndicatorStyles}>
            <span style={statusDotStyles} />
            <span style={statusTextStyles}>系统正常</span>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div style={mainLayoutStyles}>
        {/* Sidebar */}
        <aside
          style={{
            ...sidebarStyles,
            width: sidebarCollapsed ? '64px' : '220px',
          }}
        >
          <nav style={navStyles}>
            {NAV_GROUPS.map((group) => (
              <NavGroup
                key={group.group}
                group={sidebarCollapsed ? '' : group.group}
                items={group.items}
                activePath={location.pathname}
                onNavigate={handleNavigate}
              />
            ))}
          </nav>
        </aside>

        {/* Content Area */}
        <main style={contentStyles}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

// ============================================
// Styles
// ============================================

const shellStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  backgroundColor: '#F5F7FA',
  fontFamily: '"Noto Sans SC", "Segoe UI", system-ui, sans-serif',
};

const topBarStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  height: '56px',
  padding: '0 16px',
  backgroundColor: '#FFFFFF',
  borderBottom: '1px solid #E5E7EB',
  flexShrink: 0,
  zIndex: 100,
};

const topBarLeftStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
};

const menuButtonStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '36px',
  height: '36px',
  border: 'none',
  borderRadius: '6px',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  fontSize: '20px',
  color: '#374151',
};

const logoStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const logoIconStyles: React.CSSProperties = {
  fontSize: '24px',
};

const logoTextStyles: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 600,
  color: '#1F2937',
};

const versionBadgeStyles: React.CSSProperties = {
  padding: '2px 6px',
  fontSize: '11px',
  fontWeight: 500,
  color: '#1890FF',
  backgroundColor: '#E6F7FF',
  borderRadius: '4px',
};

const searchWrapperStyles: React.CSSProperties = {
  flex: 1,
  maxWidth: '480px',
  margin: '0 24px',
};

const searchContainerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  height: '36px',
  padding: '0 12px',
  backgroundColor: '#F5F7FA',
  borderRadius: '6px',
  border: '1px solid #E5E7EB',
};

const searchIconStyles: React.CSSProperties = {
  fontSize: '16px',
  marginRight: '8px',
};

const searchInputStyles: React.CSSProperties = {
  flex: 1,
  border: 'none',
  outline: 'none',
  backgroundColor: 'transparent',
  fontSize: '14px',
  color: '#1F2937',
};

const searchClearStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '20px',
  height: '20px',
  border: 'none',
  borderRadius: '50%',
  backgroundColor: '#D1D5DB',
  color: '#FFFFFF',
  fontSize: '12px',
  cursor: 'pointer',
};

const topBarRightStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
};

const statusIndicatorStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '6px 12px',
  backgroundColor: '#ECFDF5',
  borderRadius: '6px',
};

const statusDotStyles: React.CSSProperties = {
  width: '8px',
  height: '8px',
  borderRadius: '50%',
  backgroundColor: STATUS_COLORS.success,
};

const statusTextStyles: React.CSSProperties = {
  fontSize: '13px',
  color: '#065F46',
};

const mainLayoutStyles: React.CSSProperties = {
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
};

const sidebarStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#FFFFFF',
  borderRight: '1px solid #E5E7EB',
  transition: 'width 200ms ease',
  overflow: 'hidden',
};

const navStyles: React.CSSProperties = {
  flex: 1,
  padding: '16px 8px',
  overflowY: 'auto',
};

const navGroupStyles: React.CSSProperties = {
  marginBottom: '24px',
};

const navGroupTitleStyles: React.CSSProperties = {
  padding: '8px 12px',
  fontSize: '12px',
  fontWeight: 600,
  color: '#9CA3AF',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const navLinkStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  width: '100%',
  padding: '10px 12px',
  border: 'none',
  borderRadius: '6px',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'background-color 150ms',
};

const activeNavLinkStyles: React.CSSProperties = {
  backgroundColor: '#E6F7FF',
  color: '#1890FF',
};

const navIconStyles: React.CSSProperties = {
  fontSize: '18px',
  flexShrink: 0,
};

const navLabelStyles: React.CSSProperties = {
  fontSize: '14px',
  color: '#374151',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
};

const contentStyles: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  backgroundColor: '#F5F7FA',
};

export default AppShell;
