import React from 'react';
import { ThreeCardsViewModel, ThreeCardKind } from '../types/orchestrationProjection';

interface ThreeCardSummaryProps {
    projection: ThreeCardsViewModel;
}

const getCardIcon = (kind: ThreeCardKind) => {
    switch (kind) {
        case 'understanding': return '🧠';
        case 'plan': return '📋';
        case 'execution_contract': return '📜';
        default: return '🔹';
    }
};

export const ThreeCardSummary: React.FC<ThreeCardSummaryProps> = ({ projection }) => {
    return (
        <div className="three-card-summary" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginBottom: '20px'
        }}>
            {projection.cards.map((card, idx) => (
                <div key={card.kind + idx} style={{
                    background: 'var(--gm-color-card-solid)',
                    border: '1px solid var(--gm-color-card-border)',
                    borderRadius: '8px',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    boxShadow: 'var(--gm-shadow-sm)',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    cursor: 'pointer'
                }} className="l4-card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '20px' }}>{getCardIcon(card.kind)}</span>
                        <span style={{
                            fontSize: '12px',
                            fontWeight: '700',
                            color: 'var(--text-1)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em'
                        }}>
                            {card.title}
                        </span>
                        {card.confidence && (
                            <span style={{
                                marginLeft: 'auto',
                                fontSize: '10px',
                                color: 'var(--ok)',
                                fontWeight: 'bold'
                            }}>
                                {(card.confidence * 100).toFixed(0)}%
                            </span>
                        )}
                    </div>
                    <ul style={{
                        margin: 0,
                        paddingLeft: '18px',
                        fontSize: '11px',
                        color: 'var(--text-2)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px'
                    }}>
                        {card.bullets.map((bullet, bIdx) => (
                            <li key={bIdx}>{bullet}</li>
                        ))}
                    </ul>
                    {card.refs && card.refs.length > 0 && (
                        <div style={{
                            fontSize: '9px',
                            color: 'var(--text-3)',
                            marginTop: 'auto',
                            borderTop: '1px solid rgba(255,255,255,0.05)',
                            paddingTop: '8px'
                        }}>
                            REF: {card.refs.join(', ')}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default ThreeCardSummary;
