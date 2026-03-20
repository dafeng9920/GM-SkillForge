import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import {
  type CanvasState,
  type DecisionConfidence,
  type IntentState,
  type InteractionDecision,
} from './interactionDecision';
import {
  executeGovernanceOrchestration,
  previewGovernanceOrchestration,
} from '../../services/governanceOrchestrationAdapter';

export const GOVERNANCE_TURNS_STORAGE_KEY = 'gm-skillforge-home-turns-v1';

export interface InteractionTurn {
  id: string;
  userInput: string;
  intent: IntentState;
  canvas: CanvasState;
  confidence: DecisionConfidence;
  requiresClarification: boolean;
  routeTarget: string | null;
  decision: InteractionDecision;
  runId?: string;
  traceId?: string;
  confirmedAt: string;
}

interface SubmitOptions {
  intentHint?: IntentState;
}

interface GovernanceInteractionContextValue {
  draft: string;
  setDraft: (value: string) => void;
  draftIntentHint: IntentState;
  setDraftIntentHint: (intent: IntentState) => void;
  submitDraft: (options?: SubmitOptions) => Promise<InteractionTurn | null>;
  ingestExternalPrompt: (input: string, options?: SubmitOptions) => Promise<InteractionTurn | null>;
  turns: InteractionTurn[];
  latestTurn: InteractionTurn | null;
  latestTurns: InteractionTurn[];
  draftDecision: InteractionDecision | null;
  latestDecision: InteractionDecision | null;
  activeDecision: InteractionDecision;
  currentCanvas: CanvasState;
  isTyping: boolean;
  clearDraft: () => void;
}

const GovernanceInteractionContext = createContext<GovernanceInteractionContextValue | null>(null);

const normalizeTurn = (turn: Partial<InteractionTurn>): InteractionTurn | null => {
  if (!turn.id || !turn.userInput || !turn.confirmedAt) {
    return null;
  }

  const fallbackDecision = previewGovernanceOrchestration({
    input: turn.userInput,
    intentHint: (turn.intent as IntentState) ?? 'unknown',
  }).decision;
  const decision = turn.decision ?? fallbackDecision;

  return {
    id: turn.id,
    userInput: turn.userInput,
    intent: decision.intent,
    canvas: decision.canvas,
    confidence: decision.confidence,
    requiresClarification: decision.requiresClarification,
    routeTarget: decision.routeTarget,
    decision,
    runId: turn.runId ?? decision.runId,
    traceId: turn.traceId ?? decision.traceId,
    confirmedAt: turn.confirmedAt,
  };
};

export const GovernanceInteractionProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [draft, setDraftState] = useState('');
  const [draftIntentHint, setDraftIntentHint] = useState<IntentState>('unknown');
  const [turns, setTurns] = useState<InteractionTurn[]>([]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(GOVERNANCE_TURNS_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw) as Partial<InteractionTurn>[];
      if (Array.isArray(parsed)) {
        setTurns(parsed.map(normalizeTurn).filter((turn): turn is InteractionTurn => turn !== null));
      }
    } catch {
      // ignore corrupted local cache
    }
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(GOVERNANCE_TURNS_STORAGE_KEY, JSON.stringify(turns.slice(-12)));
    } catch {
      // ignore storage failures
    }
  }, [turns]);

  const setDraft = (value: string) => {
    setDraftState(value);
  };

  const clearDraft = () => {
    setDraftState('');
    setDraftIntentHint('unknown');
  };

  const latestTurn = turns.length > 0 ? turns[turns.length - 1] : null;
  const latestTurns = useMemo(() => turns.slice(-3).reverse(), [turns]);

  const submitDraft = async (options?: SubmitOptions): Promise<InteractionTurn | null> => {
    const nextValue = draft.trim();
    if (!nextValue) {
      return null;
    }

    const hint = options?.intentHint ?? draftIntentHint;
    const decision = (
      await executeGovernanceOrchestration({
      input: nextValue,
      intentHint: hint,
      currentCanvas: latestTurn?.canvas ?? null,
    })
    ).decision;
    const turn: InteractionTurn = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      userInput: nextValue,
      intent: decision.intent,
      canvas: decision.canvas,
      confidence: decision.confidence,
      requiresClarification: decision.requiresClarification,
      routeTarget: decision.routeTarget,
      decision,
      runId: decision.runId,
      traceId: decision.traceId,
      confirmedAt: new Date().toISOString(),
    };

    setTurns((current) => [...current, turn]);
    clearDraft();
    return turn;
  };

  const ingestExternalPrompt = async (input: string, options?: SubmitOptions): Promise<InteractionTurn | null> => {
    const nextValue = input.trim();
    if (!nextValue) {
      return null;
    }

    const hint = options?.intentHint ?? draftIntentHint;
    if (
      latestTurn &&
      latestTurn.userInput === nextValue &&
      latestTurn.intent === hint
    ) {
      return latestTurn;
    }

    const decision = (
      await executeGovernanceOrchestration({
        input: nextValue,
        intentHint: hint,
        currentCanvas: latestTurn?.canvas ?? null,
      })
    ).decision;

    const turn: InteractionTurn = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      userInput: nextValue,
      intent: decision.intent,
      canvas: decision.canvas,
      confidence: decision.confidence,
      requiresClarification: decision.requiresClarification,
      routeTarget: decision.routeTarget,
      decision,
      runId: decision.runId,
      traceId: decision.traceId,
      confirmedAt: new Date().toISOString(),
    };

    setTurns((current) => [...current, turn]);
    setDraftIntentHint('unknown');
    return turn;
  };
  const draftDecision = draft.trim()
    ? previewGovernanceOrchestration({
        input: draft.trim(),
        intentHint: draftIntentHint,
      }).decision
    : null;
  const latestDecision = latestTurn
    ? latestTurn.decision
    : null;
  const activeDecision =
    draftDecision ??
    latestDecision ?? {
      intent: 'unknown',
      canvas: 'home',
      confidence: 'low',
      requiresClarification: false,
      routeTarget: null,
    };

  const value = useMemo<GovernanceInteractionContextValue>(
    () => ({
      draft,
      setDraft,
      draftIntentHint,
      setDraftIntentHint,
      submitDraft,
      ingestExternalPrompt,
      turns,
      latestTurn,
      latestTurns,
      draftDecision,
      latestDecision,
      activeDecision,
      currentCanvas: activeDecision.canvas,
      isTyping: draft.trim().length > 0,
      clearDraft,
    }),
    [draft, draftIntentHint, turns, latestTurn, latestTurns, draftDecision, latestDecision, activeDecision],
  );

  return (
    <GovernanceInteractionContext.Provider value={value}>
      {children}
    </GovernanceInteractionContext.Provider>
  );
};

export const useGovernanceInteraction = (): GovernanceInteractionContextValue => {
  const context = useContext(GovernanceInteractionContext);

  if (!context) {
    throw new Error('useGovernanceInteraction must be used inside GovernanceInteractionProvider');
  }

  return context;
};

export { INTENT_ROUTE_MAP } from './interactionDecision';
