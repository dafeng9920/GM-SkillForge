import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { IntentState } from './interactionDecision';
import { useGovernanceInteraction } from './interaction';

interface UseGovernancePromptQuerySyncOptions {
  intentHint?: IntentState;
}

export function useGovernancePromptQuerySync(
  options?: UseGovernancePromptQuerySyncOptions,
): void {
  const [searchParams] = useSearchParams();
  const { latestTurn, ingestExternalPrompt } = useGovernanceInteraction();

  useEffect(() => {
    const prompt = searchParams.get('prompt')?.trim();
    if (!prompt) {
      return;
    }

    if (latestTurn?.userInput === prompt) {
      return;
    }

    void ingestExternalPrompt(prompt, {
      intentHint: options?.intentHint ?? 'unknown',
    });
  }, [ingestExternalPrompt, latestTurn?.userInput, options?.intentHint, searchParams]);
}
