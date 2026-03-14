import React from 'react';
import { Link } from 'react-router-dom';

const CARD_ITEMS = [
  {
    title: 'OpenClaw Governance Layer',
    text: '定位：不替代 OpenClaw，而是为其提供生产级治理加固层。',
  },
  {
    title: 'L3 核心能力',
    text: '裁决 + 阻断 + 审计。当前已覆盖 G1-G4，部分覆盖 G5。',
  },
  {
    title: 'PR1 交付范围',
    text: '战略首页、路由统一、Compose 安全基线收口。',
  },
];

const ACTIONS = [
  { label: '执行意图', path: '/execute/run-intent' },
  { label: '审计包', path: '/audit/packs' },
  { label: '系统健康', path: '/system/health' },
];

export const StrategyHomePage: React.FC = () => {
  return (
    <div style={styles.page}>
      <section style={styles.hero}>
        <p style={styles.kicker}>GM-SkillForge · PR1</p>
        <h1 style={styles.title}>OpenClaw 治理战略首页</h1>
        <p style={styles.subtitle}>
          目标：在不改变 OpenClaw 核心能力的前提下，建立可控、可审计、可扩展的生产治理层。
        </p>
      </section>

      <section style={styles.grid}>
        {CARD_ITEMS.map((item) => (
          <article key={item.title} style={styles.card}>
            <h2 style={styles.cardTitle}>{item.title}</h2>
            <p style={styles.cardText}>{item.text}</p>
          </article>
        ))}
      </section>

      <section style={styles.actions}>
        {ACTIONS.map((action) => (
          <Link key={action.path} to={action.path} style={styles.actionBtn}>
            进入 {action.label}
          </Link>
        ))}
      </section>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  page: {
    padding: '32px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  hero: {
    background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%)',
    color: '#f8fafc',
    borderRadius: '14px',
    padding: '28px',
  },
  kicker: {
    margin: 0,
    fontSize: '12px',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    opacity: 0.9,
  },
  title: {
    margin: '8px 0 12px',
    fontSize: '30px',
  },
  subtitle: {
    margin: 0,
    maxWidth: '820px',
    lineHeight: 1.6,
    opacity: 0.95,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '16px',
  },
  card: {
    background: '#ffffff',
    border: '1px solid #dbe3ef',
    borderRadius: '10px',
    padding: '18px',
  },
  cardTitle: {
    margin: '0 0 8px',
    fontSize: '16px',
    color: '#0f172a',
  },
  cardText: {
    margin: 0,
    fontSize: '14px',
    color: '#334155',
    lineHeight: 1.6,
  },
  actions: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
  },
  actionBtn: {
    textDecoration: 'none',
    background: '#0f766e',
    color: '#ffffff',
    borderRadius: '8px',
    padding: '10px 14px',
    fontWeight: 600,
    fontSize: '14px',
  },
};

export default StrategyHomePage;
