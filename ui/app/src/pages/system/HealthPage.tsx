/**
 * HealthPage - System Health Monitor
 *
 * Implements the System Health module with:
 * - 30s configurable polling for health checks
 * - Red/Orange/Green threshold rules
 * - Recent check details display
 *
 * @module pages/system/HealthPage
 * @see docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md Section 10.2
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ============================================
// Health Threshold Constants (Documented)
// ============================================

/** Default polling interval in milliseconds */
export const DEFAULT_POLL_INTERVAL_MS = 30000; // 30s

/** Minimum polling interval to prevent API abuse */
export const MIN_POLL_INTERVAL_MS = 5000; // 5s

/** Maximum polling interval */
export const MAX_POLL_INTERVAL_MS = 300000; // 5min

/**
 * Health status thresholds based on response time
 * - GREEN: response_time < GREEN_THRESHOLD_MS (healthy)
 * - ORANGE: GREEN_THRESHOLD_MS <= response_time < ORANGE_THRESHOLD_MS (degraded)
 * - RED: response_time >= ORANGE_THRESHOLD_MS or error (unhealthy)
 */
export const HEALTH_THRESHOLDS = {
  /** Response time < 500ms is considered healthy (GREEN) */
  GREEN_THRESHOLD_MS: 500,
  /** Response time >= 1000ms is considered degraded (ORANGE) */
  ORANGE_THRESHOLD_MS: 1000,
  /** Any error or response time >= 2000ms is unhealthy (RED) */
  RED_THRESHOLD_MS: 2000,
} as const;

/** Health status levels */
export type HealthLevel = 'GREEN' | 'ORANGE' | 'RED';

/** Route health status */
export interface RouteHealth {
  route: string;
  status: 'ok' | 'degraded' | 'error';
  response_time_ms: number;
  last_check: string;
}

/** Overall system health response */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  routes?: RouteHealth[];
  uptime_seconds?: number;
}

/** Health check history entry */
export interface HealthCheckEntry {
  id: string;
  timestamp: string;
  level: HealthLevel;
  response_time_ms: number;
  status: string;
  version: string;
  error?: string;
}

// ============================================
// Helper Functions
// ============================================

/**
 * Determine health level based on response time and status
 */
export function calculateHealthLevel(
  responseTimeMs: number,
  hasError: boolean
): HealthLevel {
  if (hasError || responseTimeMs >= HEALTH_THRESHOLDS.RED_THRESHOLD_MS) {
    return 'RED';
  }
  if (responseTimeMs >= HEALTH_THRESHOLDS.ORANGE_THRESHOLD_MS) {
    return 'ORANGE';
  }
  return 'GREEN';
}

/**
 * Get CSS color variable for health level
 */
export function getHealthColor(level: HealthLevel): string {
  switch (level) {
    case 'GREEN':
      return 'var(--ok)';
    case 'ORANGE':
      return 'var(--warn)';
    case 'RED':
      return 'var(--err)';
  }
}

/**
 * Format duration in human-readable form
 */
function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  }
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  return `${days}d ${hours}h`;
}

// ============================================
// Sub-Components
// ============================================

/** Health status indicator badge */
const HealthBadge: React.FC<{ level: HealthLevel; label?: string }> = ({
  level,
  label,
}) => {
  const colorMap: Record<HealthLevel, string> = {
    GREEN: 'var(--ok)',
    ORANGE: 'var(--warn)',
    RED: 'var(--err)',
  };

  const labelMap: Record<HealthLevel, string> = {
    GREEN: 'HEALTHY',
    ORANGE: 'DEGRADED',
    RED: 'UNHEALTHY',
  };

  return (
    <span
      className={`l4-badge l4-badge--${level === 'GREEN' ? 'ok' : level === 'ORANGE' ? 'warn' : 'err'}`}
      style={{
        background: level === 'GREEN' ? 'var(--ok-muted)' : level === 'ORANGE' ? 'var(--warn-muted)' : 'var(--err-muted)',
        color: colorMap[level],
        fontWeight: 700,
        letterSpacing: '0.05em',
      }}
    >
      {label || labelMap[level]}
    </span>
  );
};

/** Threshold configuration display */
const ThresholdInfo: React.FC = () => (
  <div className="l4-section" style={{ marginBottom: 'var(--space-3)' }}>
    <div className="l4-section__header">
      <span className="l4-section__title">Threshold Rules</span>
    </div>
    <div style={{ display: 'grid', gap: 'var(--space-2)' }}>
      <div className="l4-field" style={{ borderBottom: 'none', padding: '4px 0' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--ok)' }} />
          <span className="l4-field__label">GREEN (Healthy)</span>
        </span>
        <span className="l4-field__code" style={{ background: 'var(--ok-muted)', color: 'var(--ok)' }}>
          &lt; {HEALTH_THRESHOLDS.GREEN_THRESHOLD_MS}ms
        </span>
      </div>
      <div className="l4-field" style={{ borderBottom: 'none', padding: '4px 0' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--warn)' }} />
          <span className="l4-field__label">ORANGE (Degraded)</span>
        </span>
        <span className="l4-field__code" style={{ background: 'var(--warn-muted)', color: 'var(--warn)' }}>
          {HEALTH_THRESHOLDS.GREEN_THRESHOLD_MS}-{HEALTH_THRESHOLDS.RED_THRESHOLD_MS}ms
        </span>
      </div>
      <div className="l4-field" style={{ borderBottom: 'none', padding: '4px 0' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--err)' }} />
          <span className="l4-field__label">RED (Unhealthy)</span>
        </span>
        <span className="l4-field__code" style={{ background: 'var(--err-muted)', color: 'var(--err)' }}>
          &gt;= {HEALTH_THRESHOLDS.RED_THRESHOLD_MS}ms / Error
        </span>
      </div>
    </div>
  </div>
);

/** Route health row */
const RouteHealthRow: React.FC<{ route: RouteHealth }> = ({ route }) => {
  const level = calculateHealthLevel(route.response_time_ms, route.status === 'error');

  return (
    <div className="l4-field">
      <span className="l4-field__label" style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
        {route.route}
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <span
          className="l4-field__code"
          style={{
            background: level === 'GREEN' ? 'var(--ok-muted)' : level === 'ORANGE' ? 'var(--warn-muted)' : 'var(--err-muted)',
            color: getHealthColor(level),
          }}
        >
          {route.response_time_ms}ms
        </span>
        <HealthBadge level={level} />
      </span>
    </div>
  );
};

/** Recent check history item */
const CheckHistoryItem: React.FC<{ entry: HealthCheckEntry }> = ({ entry }) => (
  <div
    className="l4-field"
    style={{
      padding: 'var(--space-2) 0',
      borderBottom: '1px solid var(--line)',
      fontSize: 12,
    }}
  >
    <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: getHealthColor(entry.level),
        }}
      />
      <span style={{ color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>
        {new Date(entry.timestamp).toLocaleTimeString()}
      </span>
    </span>
    <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
      <span className="l4-field__code">{entry.response_time_ms}ms</span>
      <HealthBadge level={entry.level} />
    </span>
  </div>
);

// ============================================
// Main Component
// ============================================

export interface HealthPageProps {
  /** API base URL for health endpoint */
  apiBaseUrl?: string;
  /** Polling interval in milliseconds (default: 30000) */
  pollIntervalMs?: number;
  /** Maximum number of history entries to keep */
  maxHistorySize?: number;
  /** Called when health level changes */
  onHealthLevelChange?: (level: HealthLevel) => void;
}

export function HealthPage({
  apiBaseUrl = '/api/v1',
  pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
  maxHistorySize = 20,
  onHealthLevelChange,
}: HealthPageProps) {
  // State
  const [currentHealth, setCurrentHealth] = useState<HealthResponse | null>(null);
  const [currentLevel, setCurrentLevel] = useState<HealthLevel>('GREEN');
  const [responseTime, setResponseTime] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  const [history, setHistory] = useState<HealthCheckEntry[]>([]);
  const [isPolling, setIsPolling] = useState(true);
  const [configInterval, setConfigInterval] = useState(pollIntervalMs);

  // Refs
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // ============================================
  // Health Check Logic
  // ============================================

  const performHealthCheck = useCallback(async () => {
    const startTime = Date.now();
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setIsLoading(true);
    setLastError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: abortController.signal,
      });

      const endTime = Date.now();
      const respTime = endTime - startTime;
      setResponseTime(respTime);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: HealthResponse = await response.json();
      setCurrentHealth(data);

      const level = calculateHealthLevel(respTime, false);
      setCurrentLevel(level);

      // Add to history
      const entry: HealthCheckEntry = {
        id: `check-${Date.now()}`,
        timestamp: new Date().toISOString(),
        level,
        response_time_ms: respTime,
        status: data.status,
        version: data.version || 'unknown',
      };

      setHistory(prev => [entry, ...prev].slice(0, maxHistorySize));

    } catch (error) {
      const endTime = Date.now();
      const respTime = endTime - startTime;
      setResponseTime(respTime);

      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setLastError(errorMessage);
      setCurrentLevel('RED');

      const entry: HealthCheckEntry = {
        id: `check-${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: 'RED',
        response_time_ms: respTime,
        status: 'error',
        version: 'unknown',
        error: errorMessage,
      };

      setHistory(prev => [entry, ...prev].slice(0, maxHistorySize));
    } finally {
      setIsLoading(false);
    }
  }, [apiBaseUrl, maxHistorySize]);

  // Effect: Notify on level change
  useEffect(() => {
    onHealthLevelChange?.(currentLevel);
  }, [currentLevel, onHealthLevelChange]);

  // Effect: Polling
  useEffect(() => {
    if (isPolling) {
      // Immediate first check
      performHealthCheck();

      // Set up polling
      pollTimerRef.current = setInterval(performHealthCheck, configInterval);
    }

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [isPolling, configInterval, performHealthCheck]);

  // ============================================
  // Handlers
  // ============================================

  const handleManualRefresh = () => {
    performHealthCheck();
  };

  const handleTogglePolling = () => {
    setIsPolling(prev => !prev);
  };

  const handleIntervalChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newInterval = Math.max(
      MIN_POLL_INTERVAL_MS,
      Math.min(MAX_POLL_INTERVAL_MS, parseInt(e.target.value, 10))
    );
    setConfigInterval(newInterval);
  };

  // ============================================
  // Render
  // ============================================

  return (
    <div className="l4-page" style={{ padding: 'var(--space-4)', background: 'var(--bg-0)' }}>
      {/* Header */}
      <header style={{ marginBottom: 'var(--space-4)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-1)', margin: 0 }}>
            System Health Monitor
          </h1>
          <p style={{ color: 'var(--text-3)', fontSize: 13, margin: 'var(--space-1) 0 0' }}>
            Route: /system/health | Polling: {isPolling ? 'ON' : 'OFF'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
          <select
            value={configInterval}
            onChange={handleIntervalChange}
            disabled={isLoading}
            style={{
              background: 'var(--panel-2)',
              border: '1px solid var(--line)',
              color: 'var(--text-1)',
              padding: 'var(--space-2)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 12,
            }}
          >
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
            <option value={30000}>30s (default)</option>
            <option value={60000}>60s</option>
            <option value={120000}>120s</option>
          </select>
          <button
            className="l4-btn l4-btn--secondary"
            onClick={handleTogglePolling}
            disabled={isLoading}
          >
            {isPolling ? 'Pause' : 'Resume'}
          </button>
          <button
            className="l4-btn l4-btn--primary"
            onClick={handleManualRefresh}
            disabled={isLoading}
          >
            {isLoading ? 'Checking...' : 'Refresh'}
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 'var(--space-4)' }}>
        {/* Left: Status & Routes */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Current Status Card */}
          <div className="l4-card">
            <div className="l4-card__header">
              <span className="l4-card__title">Current Status</span>
              <HealthBadge level={currentLevel} />
            </div>
            <div className="l4-card__body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: getHealthColor(currentLevel) }}>
                    {responseTime}ms
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', textTransform: 'uppercase' }}>
                    Response Time
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>
                    {currentHealth?.version || '-'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', textTransform: 'uppercase' }}>
                    Version
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-1)' }}>
                    {currentHealth?.uptime_seconds ? formatDuration(currentHealth.uptime_seconds) : '-'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', textTransform: 'uppercase' }}>
                    Uptime
                  </div>
                </div>
              </div>

              {/* Error Display */}
              {lastError && (
                <div className="l4-alert l4-alert--err" style={{ marginTop: 'var(--space-3)' }}>
                  <span className="l4-alert__icon">!</span>
                  <div className="l4-alert__content">
                    <div className="l4-alert__code">ERROR</div>
                    <div className="l4-alert__message">{lastError}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Routes Health */}
          {currentHealth?.routes && currentHealth.routes.length > 0 && (
            <div className="l4-card">
              <div className="l4-card__header">
                <span className="l4-card__title">Route Health</span>
                <span className="l4-chip">{currentHealth.routes.length} routes</span>
              </div>
              <div className="l4-card__body">
                {currentHealth.routes.map((route, idx) => (
                  <RouteHealthRow key={idx} route={route} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Thresholds & History */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Threshold Rules */}
          <ThresholdInfo />

          {/* Recent Checks */}
          <div className="l4-card" style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            <div className="l4-card__header">
              <span className="l4-card__title">Recent Checks</span>
              <span className="l4-chip">{history.length} entries</span>
            </div>
            <div
              className="l4-card__body"
              style={{
                flex: 1,
                overflow: 'auto',
                maxHeight: '400px',
              }}
            >
              {history.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', padding: 'var(--space-4)' }}>
                  No checks recorded yet
                </div>
              ) : (
                history.map(entry => (
                  <CheckHistoryItem key={entry.id} entry={entry} />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HealthPage;
