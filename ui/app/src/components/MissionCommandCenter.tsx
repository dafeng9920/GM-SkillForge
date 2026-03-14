import React, { useState } from 'react';

interface MissionCommandCenterProps {
  onLaunch: (intent: string) => void;
  isLoading: boolean;
}

export const MissionCommandCenter: React.FC<MissionCommandCenterProps> = ({ onLaunch, isLoading }) => {
  const [intent, setIntent] = useState('');

  const handleLaunch = () => {
    if (intent.trim() && !isLoading) {
      onLaunch(intent);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleLaunch();
    }
  };

  return (
    <div className="mission-command-center" style={{
      padding: '20px',
      background: 'rgba(10, 17, 34, 0.4)',
      borderRadius: '12px',
      border: '1px solid var(--accent-muted)',
      marginBottom: '20px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
    }}>
      <div style={{ display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter your mission objective (e.g. Scrape Reddit for AI news)..."
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--panel-border)',
            borderRadius: '6px',
            padding: '12px 16px',
            color: 'var(--text-1)',
            fontSize: '14px',
            outline: 'none',
            transition: 'border-color 0.2s'
          }}
          className="commander-input"
        />
        <button
          onClick={handleLaunch}
          disabled={isLoading || !intent.trim()}
          style={{
            background: 'linear-gradient(135deg, var(--accent) 0%, #1e3799 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '0 24px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.2s',
            opacity: isLoading ? 0.6 : 1
          }}
          className="l4-btn"
        >
          {isLoading ? 'LAUNCHING...' : 'LAUNCH MISSION'}
        </button>
      </div>
      <div style={{ marginTop: '10px', display: 'flex', gap: '8px' }}>
        <span style={{ fontSize: '11px', color: 'var(--text-3)' }}>SUGGESTIONS:</span>
        {['Reddit Scraping', 'GitHub Audit', 'Stock Analysis'].map(s => (
          <button
            key={s}
            onClick={() => setIntent(s)}
            style={{
              background: 'transparent',
              border: '1px solid var(--line)',
              borderRadius: '4px',
              padding: '2px 8px',
              fontSize: '10px',
              color: 'var(--text-3)',
              cursor: 'pointer'
            }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
};

export default MissionCommandCenter;
