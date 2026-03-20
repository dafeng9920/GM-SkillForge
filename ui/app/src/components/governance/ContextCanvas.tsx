import React from 'react';
import type { InteractionDecision } from '../../features/governanceInteraction/interactionDecision';
import {
  buildContextCanvasModel,
  type CanvasIntentKey,
} from '../../features/governanceInteraction/canvasRegistry';
import styles from './ContextCanvas.module.css';

export interface ContextCanvasProps {
  language: 'zh' | 'en';
  decision: InteractionDecision;
  confirmedValue?: string;
  onPrimaryAction?: (decision: InteractionDecision) => void;
  onSecondaryAction?: (decision: InteractionDecision) => void;
  onAlternativeSelect?: (intent: CanvasIntentKey) => void;
}

export const ContextCanvas: React.FC<ContextCanvasProps> = ({
  language,
  decision,
  confirmedValue,
  onPrimaryAction,
  onSecondaryAction,
  onAlternativeSelect,
}) => {
  const model = buildContextCanvasModel(language, decision);
  const canAct = Boolean(confirmedValue?.trim());

  return (
    <div className={`${styles.canvas} ${styles[`canvas-${model.canvas}`] ?? ''}`}>
      <div className={styles.summaryRow}>
        <p className={styles.summary}>{model.summary}</p>
        <span className={styles.statusPill}>{model.status}</span>
      </div>

      {confirmedValue ? (
        <div className={styles.confirmedBox}>
          <span className={styles.badge}>{model.confirmedLabel}</span>
          <p>{confirmedValue}</p>
        </div>
      ) : (
        <div className={styles.emptyState}>
          <strong>{model.emptyTitle}</strong>
          <p>{model.emptyDescription}</p>
        </div>
      )}

      <div className={styles.reasonBox}>
        <span className={styles.badge}>{model.reasonLabel}</span>
        <p>{model.reasonText}</p>
        {model.profileLabel && model.profileValue ? (
          <div className={styles.profileRow}>
            <span className={styles.profileLabel}>{model.profileLabel}</span>
            <span className={styles.profileValue}>{model.profileValue}</span>
          </div>
        ) : null}
        {model.capabilitySegments && model.capabilitySegments.length > 0 ? (
          <div className={styles.capabilityGroup}>
            <span className={styles.capabilityLabel}>{model.capabilityLabel}</span>
            <div className={styles.capabilityList}>
              {model.capabilitySegments.map((item) => (
                <span key={item} className={styles.capabilityPill}>
                  {item}
                </span>
              ))}
            </div>
          </div>
        ) : null}
        {model.detailItems && model.detailItems.length > 0 ? (
          <div className={styles.detailGrid}>
            {model.detailItems.map((item) => (
              <div key={`${item.label}-${item.value}`} className={styles.detailCard}>
                <span className={styles.detailLabel}>{item.label}</span>
                <strong className={styles.detailValue}>{item.value}</strong>
              </div>
            ))}
          </div>
        ) : null}
        {model.artifactItems && model.artifactItems.length > 0 ? (
          <div className={styles.sectionGroup}>
            {model.artifactLabel ? <span className={styles.capabilityLabel}>{model.artifactLabel}</span> : null}
            <div className={styles.artifactGrid}>
              {model.artifactItems.map((item) => (
                <div
                  key={`${item.label}-${item.value}`}
                  className={`${styles.artifactCard} ${
                    item.emphasis ? styles[`artifact-${item.emphasis}`] : ''
                  }`}
                >
                  <span className={styles.detailLabel}>{item.label}</span>
                  <strong className={styles.detailValue}>{item.value}</strong>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        {model.actionItems && model.actionItems.length > 0 ? (
          <div className={styles.sectionGroup}>
            {model.actionLabel ? <span className={styles.capabilityLabel}>{model.actionLabel}</span> : null}
            <div className={styles.actionList}>
              {model.actionItems.map((item) => (
                <div key={`${item.label}-${item.value}`} className={styles.actionRow}>
                  <span className={styles.actionKey}>{item.label}</span>
                  <span className={styles.actionValue}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className={styles.layout}>
        <div className={styles.mainCard}>
          <span className={styles.badge}>{model.primaryLabel}</span>
          <h3 className={styles.mainTitle}>{model.primaryTitle}</h3>
          <p className={styles.mainText}>{model.primaryDescription}</p>
          <div className={styles.actions}>
            <button
              className={styles.primaryAction}
              type="button"
              onClick={() => onPrimaryAction?.(decision)}
              disabled={!canAct}
            >
              {model.primaryActionLabel}
            </button>
            {model.secondaryActionLabel && onSecondaryAction ? (
              <button
                className={styles.secondaryAction}
                type="button"
                onClick={() => onSecondaryAction(decision)}
                disabled={!canAct}
              >
                {model.secondaryActionLabel}
              </button>
            ) : null}
          </div>
        </div>

        <div className={styles.secondaryCard}>
          <span className={styles.badge}>{model.alternativesLabel}</span>
          <div className={styles.alternativeList}>
            {model.alternatives.map((item) => (
              <button
                key={item.key}
                type="button"
                className={`${styles.alternativePath} ${item.active ? styles.alternativePathActive : ''}`}
                onClick={() => onAlternativeSelect?.(item.key)}
              >
                <strong>{item.title}</strong>
                <span>{item.eyebrow}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
