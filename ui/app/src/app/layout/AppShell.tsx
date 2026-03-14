import React, { useCallback, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { LanguageProvider, useLanguage, type AppLanguage } from '../i18n';
import { GovernanceInteractionProvider } from '../../features/governanceInteraction/interaction';
import {
  GovernanceCanvasSlotProvider,
  GovernanceCanvasSlotRenderer,
} from '../../components/governance/GovernanceCanvasSlot';

interface NavItem {
  id: string;
  path: string;
  icon: string;
  priority: 'main' | 'secondary';
}

const NAV_LABELS: Record<AppLanguage, Record<string, string>> = {
  zh: {
    home: '首页',
    overview: '概览',
    intake: '摄入',
    audit: '审计',
    permit: '发布',
    registry: '登记',
    forge: '锻造',
    policies: '策略',
    history: '历史',
  },
  en: {
    home: 'Home',
    overview: 'Overview',
    intake: 'Intake',
    audit: 'Audit',
    permit: 'Release',
    registry: 'Registry',
    forge: 'Forge',
    policies: 'Policies',
    history: 'History',
  },
};

const GROUP_LABELS: Record<AppLanguage, Record<string, string>> = {
  zh: {
    entry: '入口',
    main: '治理主链',
    support: '治理支撑',
    archive: '策略与历史',
  },
  en: {
    entry: 'Entry',
    main: 'Governance Chain',
    support: 'Support',
    archive: 'Policies & History',
  },
};

const COPY: Record<
  AppLanguage,
  {
    collapse: string;
    expand: string;
    searchPlaceholder: string;
    clear: string;
    systemHealthy: string;
    switchLanguage: string;
  }
> = {
  zh: {
    collapse: '收起侧边栏',
    expand: '展开侧边栏',
    searchPlaceholder: '搜索证据编号、资产 ID 或许可证号...',
    clear: '清除',
    systemHealthy: '系统正常',
    switchLanguage: '切换为英文',
  },
  en: {
    collapse: 'Collapse sidebar',
    expand: 'Expand sidebar',
    searchPlaceholder: 'Search evidence ref, asset ID, or permit ID...',
    clear: 'Clear',
    systemHealthy: 'System healthy',
    switchLanguage: 'Switch to Chinese',
  },
};

const NAV_GROUPS: { groupId: keyof (typeof GROUP_LABELS)['zh']; items: NavItem[] }[] = [
  {
    groupId: 'entry',
    items: [
      { id: 'home', path: '/home', icon: '◌', priority: 'main' },
      { id: 'overview', path: '/dashboard', icon: '📊', priority: 'main' },
      { id: 'intake', path: '/intake/vetting', icon: '⇣', priority: 'main' },
    ],
  },
  {
    groupId: 'main',
    items: [
      { id: 'audit', path: '/audit/detail', icon: '🔍', priority: 'main' },
      { id: 'permit', path: '/permit', icon: '✓', priority: 'main' },
    ],
  },
  {
    groupId: 'support',
    items: [
      { id: 'registry', path: '/registry', icon: '📋', priority: 'secondary' },
      { id: 'forge', path: '/forge', icon: '🔨', priority: 'secondary' },
    ],
  },
  {
    groupId: 'archive',
    items: [
      { id: 'policies', path: '/policies', icon: '⚙️', priority: 'secondary' },
      { id: 'history', path: '/history', icon: '📜', priority: 'secondary' },
    ],
  },
];

const STATUS_COLORS = {
  success: '#10B981',
};

const GlobalSearch: React.FC<{
  value: string;
  onChange: (value: string) => void;
  onSearch: (value: string) => void;
}> = ({ value, onChange, onSearch }) => {
  const { language } = useLanguage();

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && value.trim()) {
      onSearch(value.trim());
    }
  };

  return (
    <div style={searchContainerStyles}>
      <span style={searchIconStyles}>🔍</span>
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={COPY[language].searchPlaceholder}
        style={searchInputStyles}
      />
      {value && (
        <button type="button" onClick={() => onChange('')} style={searchClearStyles} title={COPY[language].clear}>
          ✕
        </button>
      )}
    </div>
  );
};

const NavLink: React.FC<{
  item: NavItem;
  label: string;
  isActive: boolean;
  onClick: () => void;
}> = ({ item, label, isActive, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    style={{
      ...navLinkStyles,
      ...(isActive ? activeNavLinkStyles : {}),
      ...(item.priority === 'main' ? mainChainStyles : {}),
    }}
    title={label}
  >
    <span style={navIconStyles}>{item.icon}</span>
    <span style={navLabelStyles}>{label}</span>
  </button>
);

const NavGroup: React.FC<{
  groupLabel: string;
  items: NavItem[];
  activePath: string;
  language: AppLanguage;
  onNavigate: (path: string) => void;
}> = ({ groupLabel, items, activePath, language, onNavigate }) => (
  <div style={navGroupStyles}>
    <div style={navGroupTitleStyles}>{groupLabel}</div>
    {items.map((item) => (
      <NavLink
        key={item.id}
        item={item}
        label={NAV_LABELS[language][item.id]}
        isActive={activePath === item.path || activePath.startsWith(`${item.path}/`)}
        onClick={() => onNavigate(item.path)}
      />
    ))}
  </div>
);

const AppShellBody: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { language, toggleLanguage } = useLanguage();
  const [searchValue, setSearchValue] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const isHomeRoute = location.pathname === '/home';

  const handleNavigate = useCallback((path: string) => {
    navigate(path);
  }, [navigate]);

  const handleSearch = useCallback((query: string) => {
    navigate(`/audit/detail?search=${encodeURIComponent(query)}`);
  }, [navigate]);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((current) => !current);
  }, []);

  const isPathActive = useCallback((path: string) => {
    if (path === '/home') {
      return location.pathname === '/home';
    }

    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  }, [location.pathname]);

  return (
    <div style={shellStyles}>
      <style>{`
        @keyframes gmPulse {
          0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.18), 0 0 10px rgba(16,185,129,0.12); }
          70% { box-shadow: 0 0 0 6px rgba(16,185,129,0), 0 0 16px rgba(16,185,129,0.16); }
          100% { box-shadow: 0 0 0 0 rgba(16,185,129,0), 0 0 10px rgba(16,185,129,0.12); }
        }
      `}</style>
      <header style={topBarStyles}>
        <div style={topBarLeftStyles}>
          <button
            type="button"
            onClick={toggleSidebar}
            style={menuButtonStyles}
            title={sidebarCollapsed ? COPY[language].expand : COPY[language].collapse}
          >
            ☰
          </button>
          <div style={logoStyles}>
            <span style={logoIconStyles}>⚡</span>
            <span style={logoTextStyles}>SkillForge</span>
            <span style={versionBadgeStyles}>v1.0</span>
          </div>
        </div>

        {!isHomeRoute && (
          <div style={searchWrapperStyles}>
            <GlobalSearch value={searchValue} onChange={setSearchValue} onSearch={handleSearch} />
          </div>
        )}

        {isHomeRoute && (
          <nav style={headerNavStyles}>
            {NAV_GROUPS.flatMap((group) => group.items).slice(0, 7).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavigate(item.path)}
                style={{
                  ...headerNavLinkStyles,
                  ...(isPathActive(item.path) ? headerNavActiveStyles : {}),
                }}
              >
                {NAV_LABELS[language][item.id]}
              </button>
            ))}
          </nav>
        )}

        <div style={topBarRightStyles}>
          <button
            type="button"
            onClick={toggleLanguage}
            style={languageButtonStyles}
            title={COPY[language].switchLanguage}
          >
            {language === 'zh' ? 'EN' : '中'}
          </button>
          <div style={statusIndicatorStyles}>
            <span style={statusDotStyles} />
            <span style={statusTextStyles}>{COPY[language].systemHealthy}</span>
          </div>
        </div>
      </header>

      <div style={mainLayoutStyles}>
        {!isHomeRoute && (
          <aside
            style={{
              ...sidebarStyles,
              width: sidebarCollapsed ? '64px' : '220px',
            }}
          >
            <nav style={navStyles}>
              {NAV_GROUPS.map((group) => (
                <NavGroup
                  key={group.groupId}
                  groupLabel={sidebarCollapsed ? '' : GROUP_LABELS[language][group.groupId]}
                  items={group.items}
                  activePath={location.pathname}
                  language={language}
                  onNavigate={handleNavigate}
                />
              ))}
            </nav>
          </aside>
        )}

        <main style={{ ...contentStyles, ...(isHomeRoute ? homeContentStyles : {}) }}>
          {!isHomeRoute ? (
            <div style={canvasSlotStyles}>
              <GovernanceCanvasSlotRenderer />
            </div>
          ) : null}
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export const AppShell: React.FC = () => (
  <LanguageProvider>
    <GovernanceInteractionProvider>
      <GovernanceCanvasSlotProvider>
        <AppShellBody />
      </GovernanceCanvasSlotProvider>
    </GovernanceInteractionProvider>
  </LanguageProvider>
);

const shellStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  background:
    'radial-gradient(circle at top center, rgba(234,88,12,0.1), transparent 18%), linear-gradient(180deg, #050505 0%, #09090b 100%)',
  fontFamily: '"Noto Sans SC", "Segoe UI", system-ui, sans-serif',
};

const topBarStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  height: '64px',
  padding: '0 18px 0 16px',
  background:
    'linear-gradient(135deg, rgba(9,9,11,0.98) 0%, rgba(16,16,16,0.96) 75%, rgba(34,20,12,0.92) 100%)',
  borderBottom: '1px solid rgba(255,255,255,0.06)',
  boxShadow: 'inset 0 -1px 0 rgba(255,255,255,0.02), 0 10px 30px rgba(0,0,0,0.24)',
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
  width: '38px',
  height: '38px',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: '12px',
  backgroundColor: 'rgba(255,255,255,0.02)',
  cursor: 'pointer',
  fontSize: '18px',
  color: '#e7e5e4',
};

const logoStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
};

const logoIconStyles: React.CSSProperties = {
  fontSize: '24px',
};

const logoTextStyles: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 800,
  letterSpacing: '-0.02em',
  color: '#f5f5f4',
};

const versionBadgeStyles: React.CSSProperties = {
  padding: '3px 8px',
  fontSize: '11px',
  fontWeight: 700,
  color: '#fdba74',
  backgroundColor: 'rgba(217,119,6,0.12)',
  borderRadius: '999px',
  border: '1px solid rgba(217,119,6,0.2)',
};

const searchWrapperStyles: React.CSSProperties = {
  flex: 1,
  maxWidth: '480px',
  margin: '0 24px',
};

const headerNavStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  flex: 1,
  justifyContent: 'center',
  margin: '0 20px',
};

const headerNavLinkStyles: React.CSSProperties = {
  appearance: 'none',
  border: '1px solid transparent',
  background: 'transparent',
  color: '#a8a29e',
  borderRadius: '999px',
  padding: '8px 11px',
  fontSize: '12px',
  fontWeight: 700,
  letterSpacing: '0.04em',
  cursor: 'pointer',
};

const headerNavActiveStyles: React.CSSProperties = {
  border: '1px solid rgba(234,88,12,0.24)',
  background: 'linear-gradient(180deg, rgba(234,88,12,0.12) 0%, rgba(234,88,12,0.06) 100%)',
  color: '#f5f5f4',
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03), 0 0 0 1px rgba(234,88,12,0.04)',
};

const searchContainerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  height: '40px',
  padding: '0 12px',
  backgroundColor: 'rgba(255,255,255,0.03)',
  borderRadius: '10px',
  border: '1px solid rgba(255,255,255,0.08)',
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
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
  color: '#f5f5f4',
};

const searchClearStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '20px',
  height: '20px',
  border: 'none',
  borderRadius: '50%',
  backgroundColor: 'rgba(255,255,255,0.1)',
  color: '#f5f5f4',
  fontSize: '12px',
  cursor: 'pointer',
};

const topBarRightStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
};

const languageButtonStyles: React.CSSProperties = {
  appearance: 'none',
  border: '1px solid rgba(255,255,255,0.1)',
  background: 'rgba(20, 20, 20, 0.8)',
  color: '#e7e5e4',
  borderRadius: '999px',
  padding: '8px 12px',
  fontSize: '12px',
  fontWeight: 800,
  letterSpacing: '0.08em',
  cursor: 'pointer',
};

const statusIndicatorStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 12px',
  backgroundColor: 'rgba(20,20,20,0.78)',
  borderRadius: '999px',
  border: '1px solid rgba(255,255,255,0.08)',
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03)',
};

const statusDotStyles: React.CSSProperties = {
  width: '8px',
  height: '8px',
  borderRadius: '50%',
  backgroundColor: STATUS_COLORS.success,
  boxShadow: '0 0 0 4px rgba(16,185,129,0.12), 0 0 14px rgba(16,185,129,0.18)',
  animation: 'gmPulse 2.4s ease-in-out infinite',
};

const statusTextStyles: React.CSSProperties = {
  fontSize: '13px',
  color: '#d6d3d1',
};

const mainLayoutStyles: React.CSSProperties = {
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
};

const sidebarStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  background: 'linear-gradient(180deg, rgba(8,8,8,0.98) 0%, rgba(13,13,15,1) 100%)',
  borderRight: '1px solid rgba(255,255,255,0.06)',
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
  color: '#736b63',
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
  borderRadius: '12px',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'background-color 150ms, transform 150ms',
  color: '#d6d3d1',
};

const activeNavLinkStyles: React.CSSProperties = {
  background: 'linear-gradient(90deg, rgba(234,88,12,0.18) 0%, rgba(234,88,12,0.06) 100%)',
  color: '#f5f5f4',
  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.02)',
};

const mainChainStyles: React.CSSProperties = {
  fontWeight: 600,
};

const navIconStyles: React.CSSProperties = {
  fontSize: '18px',
  flexShrink: 0,
};

const navLabelStyles: React.CSSProperties = {
  fontSize: '14px',
  color: 'inherit',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
};

const contentStyles: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  background: 'linear-gradient(180deg, #050505 0%, #09090b 100%)',
};

const homeContentStyles: React.CSSProperties = {
  background: 'linear-gradient(180deg, #050505 0%, #09090b 100%)',
};

const canvasSlotStyles: React.CSSProperties = {
  padding: '24px 24px 0',
};

export default AppShell;
