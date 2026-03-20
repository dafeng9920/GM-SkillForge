import {
  resolveInteractionDecision,
  type DecisionArtifactRefs,
  type InteractionDecision,
  type IntentState,
} from '../features/governanceInteraction/interactionDecision';

export interface GovernanceOrchestrationRequest {
  input: string;
  intentHint?: IntentState;
  locale?: 'zh' | 'en';
  currentCanvas?: string | null;
}

export interface GovernanceOrchestrationResponse {
  decision: InteractionDecision;
  orchestration_source: 'api' | 'local-fallback';
  trace: {
    input_length: number;
    intent_hint: IntentState;
    locale: 'zh' | 'en';
    backend_status?: number;
  };
}

export interface GovernanceOrchestrationApiRequest {
  raw_input: string;
  intent_hint: IntentState;
  locale: 'zh' | 'en';
  current_canvas: string | null;
}

export interface GovernanceOrchestrationApiResponse {
  decision: InteractionDecision;
  trace?: {
    run_id?: string;
    trace_id?: string;
    locale?: 'zh' | 'en';
    current_canvas?: string | null;
    input_length?: number;
  };
  artifact_refs?: DecisionArtifactRefs;
  run_id?: string;
}

/**
 * Frontend-side orchestration adapter.
 *
 * Current phase:
 * - Uses deterministic local resolver as fallback.
 * - Preserves a single integration point so backend orchestration
 *   can replace the local path without changing page components.
 */
function buildFallbackResponse(
  request: GovernanceOrchestrationRequest,
  backendStatus?: number,
): GovernanceOrchestrationResponse {
  const intentHint = request.intentHint ?? 'unknown';
  const decision = resolveInteractionDecision(request.input, intentHint);

  return {
    decision,
    orchestration_source: 'local-fallback',
    trace: {
      input_length: request.input.trim().length,
      intent_hint: intentHint,
      locale: request.locale ?? 'zh',
      ...(backendStatus ? { backend_status: backendStatus } : {}),
    },
  };
}

export function previewGovernanceOrchestration(
  request: GovernanceOrchestrationRequest,
): GovernanceOrchestrationResponse {
  return buildFallbackResponse(request);
}

export async function executeGovernanceOrchestration(
  request: GovernanceOrchestrationRequest,
): Promise<GovernanceOrchestrationResponse> {
  const payload: GovernanceOrchestrationApiRequest = {
    raw_input: request.input,
    intent_hint: request.intentHint ?? 'unknown',
    locale: request.locale ?? 'zh',
    current_canvas: request.currentCanvas ?? null,
  };

  try {
    const response = await fetch('/api/v1/governance/orchestrate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = (await response.json()) as GovernanceOrchestrationApiResponse;
      const decision: InteractionDecision = {
        ...data.decision,
        ...(data.trace?.run_id || data.run_id ? { runId: data.trace?.run_id ?? data.run_id } : {}),
        ...(data.trace?.trace_id ? { traceId: data.trace.trace_id } : {}),
        ...(data.artifact_refs ? { artifactRefs: data.artifact_refs } : {}),
      };

      return {
        decision,
        orchestration_source: 'api',
        trace: {
          input_length: request.input.trim().length,
          intent_hint: payload.intent_hint,
          locale: payload.locale,
          backend_status: response.status,
        },
      };
    }

    return buildFallbackResponse(request, response.status);
  } catch {
    return buildFallbackResponse(request);
  }
}
