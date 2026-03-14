import React from 'react';
import { FiveStageViewModel, FiveStageStatus } from '../types/orchestrationProjection';

interface FiveStageTracerProps {
    projection: FiveStageViewModel;
}

const getStatusColor = (status: FiveStageStatus) => {
    switch (status) {
        case 'success': return 'var(--ok)';
        case 'failed': return 'var(--err)';
        case 'running': return 'var(--accent)';
        case 'blocked': return 'var(--warn)';
        case 'idle':
        default: return 'var(--text-3)';
    }
};

const getStatusIcon = (status: FiveStageStatus) => {
    switch (status) {
        case 'success': return '✓';
        case 'failed': return '✗';
        case 'running': return '⋯';
        case 'blocked': return '⚠';
        case 'idle':
        default: return '○';
    }
};

export const FiveStageTracer: React.FC<FiveStageTracerProps> = ({ projection }) => {
    return (
        <div className="five-stage-tracer" style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px',
            background: 'rgba(255,255,255,0.02)',
            borderRadius: '8px',
            border: '1px solid var(--panel-border)',
            marginBottom: '20px'
        }}>
            {projection.stages.map((stage, idx) => (
                <React.Fragment key={stage.id}>
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '8px',
                        flex: 1
                    }}>
                        <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(0,0,0,0.3)',
                            border: `2px solid ${getStatusColor(stage.status)}`,
                            color: getStatusColor(stage.status),
                            fontSize: '12px',
                            fontWeight: 'bold',
                            boxShadow: stage.status === 'running' ? `0 0 10px ${getStatusColor(stage.status)}` : 'none',
                            animation: stage.status === 'running' ? 'pulse-glow 2s infinite' : 'none'
                        }}>
                            {getStatusIcon(stage.status)}
                        </div>
                        <div style={{
                            fontSize: '10px',
                            fontWeight: '600',
                            color: getStatusColor(stage.status),
                            textAlign: 'center',
                            textTransform: 'uppercase'
                        }}>
                            {stage.title}
                        </div>
                        <div style={{
                            fontSize: '9px',
                            color: 'var(--text-3)',
                            textAlign: 'center',
                            maxWidth: '80px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}>
                            {stage.summary}
                        </div>
                    </div>
                    {idx < projection.stages.length - 1 && (
                        <div style={{
                            flex: 0.5,
                            height: '1px',
                            background: 'var(--line)',
                            marginTop: '-24px'
                        }} />
                    )}
                </React.Fragment>
            ))}
            <style>{`
        @keyframes pulse-glow {
          0% { box-shadow: 0 0 0px var(--accent); opacity: 0.8; }
          50% { box-shadow: 0 0 15px var(--accent); opacity: 1; }
          100% { box-shadow: 0 0 0px var(--accent); opacity: 0.8; }
        }
      `}</style>
        </div>
    );
};

export default FiveStageTracer;
