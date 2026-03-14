import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { useLanguage } from '../../app/i18n';
import { ContextCanvasHost, type ContextCanvasHistoryItem } from './ContextCanvasHost';
import type { GovernComposerProps } from './GovernComposer';
import type { InteractionDecision } from '../../features/governanceInteraction/orchestrator';

export interface GovernanceCanvasSlotConfig {
  variant?: 'home' | 'workspace' | 'context';
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

interface GovernanceCanvasSlotContextValue {
  setSlot: (config: GovernanceCanvasSlotConfig | null) => void;
  slotConfig: GovernanceCanvasSlotConfig | null;
}

const GovernanceCanvasSlotContext = createContext<GovernanceCanvasSlotContextValue | null>(null);

export const GovernanceCanvasSlotProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [slotConfig, setSlotConfig] = useState<GovernanceCanvasSlotConfig | null>(null);

  const value = useMemo<GovernanceCanvasSlotContextValue>(
    () => ({
      setSlot: setSlotConfig,
      slotConfig,
    }),
    [slotConfig],
  );

  return (
    <GovernanceCanvasSlotContext.Provider value={value}>
      {children}
    </GovernanceCanvasSlotContext.Provider>
  );
};

export const GovernanceCanvasSlotRenderer: React.FC = () => {
  const context = useContext(GovernanceCanvasSlotContext);
  const { language } = useLanguage();

  if (!context?.slotConfig) {
    return null;
  }

  return <ContextCanvasHost language={language} {...context.slotConfig} />;
};

export const useGovernanceCanvasSlot = (config: GovernanceCanvasSlotConfig | null): void => {
  const context = useContext(GovernanceCanvasSlotContext);

  if (!context) {
    throw new Error('useGovernanceCanvasSlot must be used inside GovernanceCanvasSlotProvider');
  }

  useEffect(() => {
    context.setSlot(config);

    return () => {
      context.setSlot(null);
    };
  }, [config, context]);
};
