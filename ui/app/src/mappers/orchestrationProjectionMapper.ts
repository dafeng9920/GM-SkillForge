import type {
  FetchPackResponse,
  FiveStageItem,
  GateDecision,
  OrchestrationProjection,
  QueryRagResponse,
  RunIntentResponse,
  ThreeCard,
} from '../types/orchestrationProjection';

export interface ProjectionMapperInput {
  runIntent: RunIntentResponse;
  fetchPack?: FetchPackResponse;
  queryRag?: QueryRagResponse;
}

function normalizeDecision(value: string | undefined): GateDecision {
  if (value === 'ALLOW' || value === 'BLOCK' || value === 'DENY' || value === 'REQUIRES_CHANGES') {
    return value;
  }
  return 'BLOCK';
}

function buildTriggerStage(runId: string): FiveStageItem {
  return {
    id: 'trigger',
    title: 'Trigger',
    status: 'success',
    summary: 'run_intent request accepted',
    refs: [runId],
  };
}

function buildCollectStage(
  runIntent: RunIntentResponse,
  fetchPack?: FetchPackResponse,
): FiveStageItem {
  if (!runIntent.ok) {
    return {
      id: 'collect',
      title: 'Collect',
      status: 'idle',
      summary: 'Skipped after gate block',
    };
  }
  if (!fetchPack) {
    return {
      id: 'collect',
      title: 'Collect',
      status: 'running',
      summary: 'Waiting for fetch_pack',
    };
  }
  if (!fetchPack.ok) {
    return {
      id: 'collect',
      title: 'Collect',
      status: 'failed',
      summary: `${fetchPack.error_code}: ${fetchPack.message}`,
      refs: [fetchPack.error_code],
      payload: { blocked_by: fetchPack.blocked_by },
    };
  }
  return {
    id: 'collect',
    title: 'Collect',
    status: 'success',
    summary: 'AuditPack fetched',
    refs: [fetchPack.evidence_ref],
    payload: fetchPack.data,
  };
}

function buildProcessStage(
  runIntent: RunIntentResponse,
  queryRag?: QueryRagResponse,
): FiveStageItem {
  if (!runIntent.ok) {
    return {
      id: 'process',
      title: 'Process',
      status: 'idle',
      summary: 'Skipped after gate block',
    };
  }
  if (!queryRag) {
    return {
      id: 'process',
      title: 'Process',
      status: 'running',
      summary: 'Waiting for query_rag',
    };
  }
  if (!queryRag.ok) {
    return {
      id: 'process',
      title: 'Process',
      status: 'failed',
      summary: `${queryRag.error_code}: ${queryRag.message}`,
      refs: [queryRag.error_code],
      payload: { blocked_by: queryRag.blocked_by },
    };
  }
  return {
    id: 'process',
    title: 'Process',
    status: 'success',
    summary: 'RAG query completed',
    refs: [queryRag.evidence_ref],
    payload: queryRag.data,
  };
}

function buildDeliverStage(runIntent: RunIntentResponse): FiveStageItem {
  if (!runIntent.ok) {
    return {
      id: 'deliver',
      title: 'Deliver',
      status: 'blocked',
      summary: `${runIntent.error_code}: ${runIntent.message}`,
      refs: [runIntent.error_code],
      payload: { blocked_by: runIntent.blocked_by },
    };
  }
  const decision = normalizeDecision(runIntent.gate_decision);
  const allowed = runIntent.release_allowed === true && decision === 'ALLOW';
  return {
    id: 'deliver',
    title: 'Deliver',
    status: allowed ? 'success' : 'blocked',
    summary: `gate_decision=${decision}, release_allowed=${String(runIntent.release_allowed)}`,
    refs: [decision],
    payload: { gate_decision: decision, release_allowed: runIntent.release_allowed },
  };
}

function buildReportStage(runIntent: RunIntentResponse): FiveStageItem {
  if (!runIntent.ok) {
    return {
      id: 'report',
      title: 'Report',
      status: 'success',
      summary: 'Block evidence recorded',
      refs: [runIntent.evidence_ref ?? runIntent.run_id],
    };
  }
  return {
    id: 'report',
    title: 'Report',
    status: 'success',
    summary: 'Evidence anchored and auditable',
    refs: [runIntent.evidence_ref, runIntent.run_id],
  };
}

function buildUnderstandingCard(runIntent: RunIntentResponse): ThreeCard {
  if (!runIntent.ok) {
    return {
      kind: 'understanding',
      title: '理解卡',
      bullets: [
        'Request was received by orchestration endpoint',
        `Error: ${runIntent.error_code}`,
        `Blocked by: ${runIntent.blocked_by}`,
      ],
      refs: [runIntent.run_id],
    };
  }
  return {
    kind: 'understanding',
    title: '理解卡',
    bullets: [
      `intent_id: ${runIntent.data.intent_id}`,
      `repo: ${runIntent.data.repo_url}`,
      `commit: ${runIntent.data.commit_sha}`,
      `at_time: ${runIntent.data.at_time ?? 'N/A'}`,
    ],
    refs: [runIntent.run_id],
    payload: runIntent.data as unknown as Record<string, unknown>,
  };
}

function buildPlanCard(fetchPack?: FetchPackResponse, queryRag?: QueryRagResponse): ThreeCard {
  const bullets: string[] = ['run_intent -> fetch_pack -> query_rag'];
  const refs: string[] = [];

  if (fetchPack) {
    if (fetchPack.ok) {
      bullets.push('fetch_pack succeeded');
      if (fetchPack.data.replay_pointer?.at_time) {
        bullets.push(`replay at_time: ${fetchPack.data.replay_pointer.at_time}`);
      }
      refs.push(fetchPack.evidence_ref);
    } else {
      bullets.push(`fetch_pack failed: ${fetchPack.error_code}`);
      refs.push(fetchPack.error_code);
    }
  }

  if (queryRag) {
    if (queryRag.ok) {
      bullets.push(`query_rag succeeded: ${queryRag.data.results?.length ?? 0} results`);
      refs.push(queryRag.evidence_ref);
    } else {
      bullets.push(`query_rag failed: ${queryRag.error_code}`);
      refs.push(queryRag.error_code);
    }
  }

  return {
    kind: 'plan',
    title: '方案卡',
    bullets,
    refs,
    payload: {
      fetch_pack: fetchPack,
      query_rag: queryRag,
    },
  };
}

function buildExecutionContractCard(runIntent: RunIntentResponse): ThreeCard {
  if (!runIntent.ok) {
    return {
      kind: 'execution_contract',
      title: '执行契约卡',
      bullets: [
        'gate_decision: BLOCK',
        `error_code: ${runIntent.error_code}`,
        `blocked_by: ${runIntent.blocked_by}`,
      ],
      refs: [runIntent.evidence_ref ?? runIntent.run_id],
    };
  }

  const decision = normalizeDecision(runIntent.gate_decision);
  return {
    kind: 'execution_contract',
    title: '执行契约卡',
    bullets: [
      `gate_decision: ${decision}`,
      `release_allowed: ${String(runIntent.release_allowed)}`,
      `permit_id: ${runIntent.data.permit_id ?? 'N/A'}`,
    ],
    refs: [runIntent.evidence_ref],
    payload: {
      permit_id: runIntent.data.permit_id ?? null,
      validation_timestamp: runIntent.data.validation_timestamp ?? null,
    },
  };
}

/**
 * Build frontend projection from real API responses.
 * This is a compatibility mapper until backend provides native
 * five_stage_plan / three_cards fields.
 */
export function mapToOrchestrationProjection(input: ProjectionMapperInput): OrchestrationProjection {
  const { runIntent, fetchPack, queryRag } = input;

  const runId = runIntent.run_id;
  const evidenceRef = runIntent.evidence_ref;
  const gateDecision = runIntent.ok ? normalizeDecision(runIntent.gate_decision) : 'BLOCK';
  const releaseAllowed = runIntent.ok ? runIntent.release_allowed : false;

  const stages: FiveStageItem[] = [
    buildTriggerStage(runId),
    buildCollectStage(runIntent, fetchPack),
    buildProcessStage(runIntent, queryRag),
    buildDeliverStage(runIntent),
    buildReportStage(runIntent),
  ];

  const cards: ThreeCard[] = [
    buildUnderstandingCard(runIntent),
    buildPlanCard(fetchPack, queryRag),
    buildExecutionContractCard(runIntent),
  ];

  return {
    run_id: runId,
    evidence_ref: evidenceRef,
    gate_decision: gateDecision,
    release_allowed: releaseAllowed,
    five_stage: {
      run_id: runId,
      evidence_ref: evidenceRef,
      stages,
    },
    three_cards: {
      run_id: runId,
      evidence_ref: evidenceRef,
      cards,
    },
  };
}
