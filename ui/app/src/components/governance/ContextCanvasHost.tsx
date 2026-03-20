import React from 'react';
import { ContextCanvas } from './ContextCanvas';
import { GovernComposer, type GovernComposerProps } from './GovernComposer';
import type { InteractionDecision } from '../../features/governanceInteraction/interactionDecision';
import styles from './ContextCanvasHost.module.css';

export interface ContextCanvasHistoryItem {
  id: string;
  input: string;
  state: string;
}

interface ContextCanvasHostProps {
  variant?: 'home' | 'workspace' | 'context';
  language: 'zh' | 'en';
  composer: GovernComposerProps;
  decision: InteractionDecision;
  confirmedValue?: string;
  showCanvas?: boolean;
  showHistory?: boolean;
  history?: {
    title: string;
    subtitle?: string;
    items: ContextCanvasHistoryItem[];
  };
  consoleHeader?: {
    eyebrow?: string;
    title?: string;
    meta?: string;
  };
  consoleHint?: string;
  canvasHeader?: {
    eyebrow?: string;
    title?: string;
    status?: string;
  };
  onPrimaryAction?: (decision: InteractionDecision) => void;
  onSecondaryAction?: (decision: InteractionDecision) => void;
  onAlternativeSelect?: (intent: 'vetting' | 'audit' | 'permit') => void;
}

const HistoryList: React.FC<NonNullable<ContextCanvasHostProps['history']>> = ({
  title,
  subtitle,
  items,
}) => (
  <div className={styles.historyBlock}>
    <div className={styles.historyHeader}>
      <strong>{title}</strong>
      {subtitle ? <span>{subtitle}</span> : null}
    </div>
    <div className={styles.historyList}>
      {items.map((item) => (
        <div key={item.id} className={styles.historyItem}>
          <span className={styles.historyInput}>{item.input}</span>
          <span className={styles.historyState}>{item.state}</span>
        </div>
      ))}
    </div>
  </div>
);

export const ContextCanvasHost: React.FC<ContextCanvasHostProps> = ({
  variant = 'home',
  language,
  composer,
  decision,
  confirmedValue,
  showCanvas = false,
  showHistory = false,
  history,
  consoleHeader,
  consoleHint,
  canvasHeader,
  onPrimaryAction,
  onSecondaryAction,
  onAlternativeSelect,
}) => {
  const shouldRenderHistory = Boolean(showHistory && history && history.items.length > 0);

  return (
    <section
      className={`${styles.host} ${
        variant === 'workspace'
          ? styles.hostWorkspace
          : variant === 'context'
            ? styles.hostContext
            : styles.hostHome
      }`}
    >
      <article className={styles.consolePanel}>
        {(consoleHeader?.eyebrow || consoleHeader?.title || consoleHeader?.meta) && (
          <div className={styles.consoleHeader}>
            <div>
              {consoleHeader.eyebrow ? <p className={styles.eyebrow}>{consoleHeader.eyebrow}</p> : null}
              {consoleHeader.title ? <h2 className={styles.consoleTitle}>{consoleHeader.title}</h2> : null}
            </div>
            {consoleHeader.meta ? <span className={styles.consoleMeta}>{consoleHeader.meta}</span> : null}
          </div>
        )}

        {(variant === 'home' || variant === 'context') && showCanvas ? (
          <div className={styles.homeCanvasBlock}>
            <ContextCanvas
              language={language}
              decision={decision}
              confirmedValue={confirmedValue}
              onPrimaryAction={onPrimaryAction}
              onSecondaryAction={onSecondaryAction}
              onAlternativeSelect={onAlternativeSelect}
            />
          </div>
        ) : null}

        {(variant === 'home' || variant === 'context') && shouldRenderHistory && history ? <HistoryList {...history} /> : null}

        <GovernComposer {...composer} />

        {consoleHint ? <div className={styles.consoleHint}>{consoleHint}</div> : null}

        {variant === 'workspace' && shouldRenderHistory && history ? <HistoryList {...history} /> : null}
      </article>

      {variant === 'workspace' ? (
        <article className={styles.canvasPanel}>
          {(canvasHeader?.eyebrow || canvasHeader?.title || canvasHeader?.status) && (
            <div className={styles.canvasHeader}>
              <div>
                {canvasHeader.eyebrow ? <p className={styles.eyebrow}>{canvasHeader.eyebrow}</p> : null}
                {canvasHeader.title ? <h2 className={styles.canvasTitle}>{canvasHeader.title}</h2> : null}
              </div>
              {canvasHeader.status ? <span className={styles.canvasStatus}>{canvasHeader.status}</span> : null}
            </div>
          )}

          <ContextCanvas
            language={language}
            decision={decision}
            confirmedValue={confirmedValue}
            onPrimaryAction={onPrimaryAction}
            onSecondaryAction={onSecondaryAction}
            onAlternativeSelect={onAlternativeSelect}
          />
        </article>
      ) : null}
    </section>
  );
};
