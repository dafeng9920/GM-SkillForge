import type {
  FetchPackResponse,
  OrchestrationProjection,
  QueryRagResponse,
  RunIntentResponse,
} from '../types/orchestrationProjection';

export const mockRunIntentAllow: RunIntentResponse = {
  ok: true,
  data: {
    intent_id: 'cognition_10d',
    repo_url: 'https://github.com/your-org/GM-SkillForge',
    commit_sha: 'a1b2c3d4e5f6789012345678901234567890abcd',
    at_time: '2026-02-20T14:30:00Z',
    execution_status: 'COMPLETED',
    permit_id: 'PERMIT-20260220-E36C8E21',
    validation_timestamp: '2026-02-20T08:02:26Z',
    context: null,
  },
  gate_decision: 'ALLOW',
  release_allowed: true,
  evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
  run_id: 'RUN-N8N-1771574546-AFCB903B',
};

export const mockFetchPackAllow: FetchPackResponse = {
  ok: true,
  data: {
    run_id: 'RUN-N8N-1771574546-AFCB903B',
    evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
    replay_pointer: {
      snapshot_ref: 'SNAP-001',
      at_time: '2026-02-20T14:30:00Z',
      revision: 'v1',
      evidence_bundle_ref: 'BUNDLE-001',
    },
    query_at_time: '2026-02-20T14:30:00Z',
    fetched_at: '2026-02-20T08:03:10Z',
  },
  gate_decision: 'ALLOW',
  release_allowed: true,
  evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
  run_id: 'RUN-N8N-1771574546-AFCB903B',
};

export const mockQueryRagAllow: QueryRagResponse = {
  ok: true,
  data: {
    query: 'permit issuance flow',
    results: [
      {
        id: 'rag-1',
        score: 0.93,
        text: 'Permit is issued internally by SkillForge, not by n8n.',
        source: 'docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md',
      },
      {
        id: 'rag-2',
        score: 0.89,
        text: 'Forbidden fields from n8n are rejected and logged as evidence.',
        source: 'skillforge/src/api/routes/n8n_orchestration.py',
      },
    ],
    replay_pointer: {
      at_time: '2026-02-20T14:30:00Z',
    },
  },
  gate_decision: 'ALLOW',
  release_allowed: true,
  evidence_ref: 'EV-N8N-RAG-1771575679-F2E0C7E0',
  run_id: 'RUN-N8N-1771574546-AFCB903B',
};

export const mockRunIntentBlocked: RunIntentResponse = {
  ok: false,
  error_code: 'N8N_MEMBERSHIP_DENIED',
  blocked_by: 'MEMBERSHIP_CAPABILITY_DENIED',
  message: 'Membership policy denied execution',
  evidence_ref: 'EV-N8N-INTENT-1771575625-52EA8383',
  run_id: 'RUN-N8N-1771575625-F83CCA6E',
};

export const mockProjectionAllow: OrchestrationProjection = {
  run_id: 'RUN-N8N-1771574546-AFCB903B',
  evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
  gate_decision: 'ALLOW',
  release_allowed: true,
  five_stage: {
    run_id: 'RUN-N8N-1771574546-AFCB903B',
    evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
    stages: [
      {
        id: 'trigger',
        title: 'Trigger',
        status: 'success',
        summary: 'run_intent accepted and executed',
        refs: ['RUN-N8N-1771574546-AFCB903B'],
        payload: { endpoint: '/api/v1/n8n/run_intent' },
      },
      {
        id: 'collect',
        title: 'Collect',
        status: 'success',
        summary: 'AuditPack fetched',
        refs: ['EV-N8N-INTENT-1771574546-40089F13'],
        payload: { endpoint: '/api/v1/n8n/fetch_pack' },
      },
      {
        id: 'process',
        title: 'Process',
        status: 'success',
        summary: 'RAG query completed with at_time replay',
        refs: ['EV-N8N-RAG-1771575679-F2E0C7E0'],
        payload: { endpoint: '/api/v1/n8n/query_rag' },
      },
      {
        id: 'deliver',
        title: 'Deliver',
        status: 'success',
        summary: 'Gate decision ALLOW',
        refs: ['ALLOW'],
        payload: { gate_decision: 'ALLOW', release_allowed: true },
      },
      {
        id: 'report',
        title: 'Report',
        status: 'success',
        summary: 'Evidence anchored and ready for audit',
        refs: ['RUN-N8N-1771574546-AFCB903B', 'EV-N8N-INTENT-1771574546-40089F13'],
      },
    ],
  },
  three_cards: {
    run_id: 'RUN-N8N-1771574546-AFCB903B',
    evidence_ref: 'EV-N8N-INTENT-1771574546-40089F13',
    cards: [
      {
        kind: 'understanding',
        title: '理解卡',
        bullets: [
          'Repo: your-org/GM-SkillForge',
          'Intent: cognition_10d',
          'Replay at_time: 2026-02-20T14:30:00Z',
        ],
        refs: ['RUN-N8N-1771574546-AFCB903B'],
      },
      {
        kind: 'plan',
        title: '方案卡',
        bullets: [
          'run_intent -> fetch_pack -> query_rag',
          'Fail-Closed boundary preserved',
          'Evidence and replay pointer available',
        ],
        refs: ['EV-N8N-INTENT-1771574546-40089F13', 'EV-N8N-RAG-1771575679-F2E0C7E0'],
      },
      {
        kind: 'execution_contract',
        title: '执行契约卡',
        bullets: [
          'gate_decision: ALLOW',
          'release_allowed: true',
          'permit_id: PERMIT-20260220-E36C8E21',
        ],
        refs: ['PERMIT-20260220-E36C8E21'],
      },
    ],
  },
};

export const mockProjectionBlocked: OrchestrationProjection = {
  run_id: 'RUN-N8N-1771575625-F83CCA6E',
  evidence_ref: 'EV-N8N-INTENT-1771575625-52EA8383',
  gate_decision: 'BLOCK',
  release_allowed: false,
  five_stage: {
    run_id: 'RUN-N8N-1771575625-F83CCA6E',
    evidence_ref: 'EV-N8N-INTENT-1771575625-52EA8383',
    stages: [
      {
        id: 'trigger',
        title: 'Trigger',
        status: 'success',
        summary: 'Request accepted',
      },
      {
        id: 'collect',
        title: 'Collect',
        status: 'idle',
        summary: 'Skipped after gate block',
      },
      {
        id: 'process',
        title: 'Process',
        status: 'idle',
        summary: 'Skipped after gate block',
      },
      {
        id: 'deliver',
        title: 'Deliver',
        status: 'blocked',
        summary: 'Blocked by membership policy',
        refs: ['N8N_MEMBERSHIP_DENIED'],
        payload: { blocked_by: 'MEMBERSHIP_CAPABILITY_DENIED' },
      },
      {
        id: 'report',
        title: 'Report',
        status: 'success',
        summary: 'Block evidence recorded',
        refs: ['EV-N8N-INTENT-1771575625-52EA8383'],
      },
    ],
  },
  three_cards: {
    run_id: 'RUN-N8N-1771575625-F83CCA6E',
    evidence_ref: 'EV-N8N-INTENT-1771575625-52EA8383',
    cards: [
      {
        kind: 'understanding',
        title: '理解卡',
        bullets: ['Request routed from n8n', 'Tier lacks EXECUTE_VIA_N8N capability'],
      },
      {
        kind: 'plan',
        title: '方案卡',
        bullets: ['Upgrade membership tier', 'Retry run_intent without forbidden fields'],
      },
      {
        kind: 'execution_contract',
        title: '执行契约卡',
        bullets: [
          'gate_decision: BLOCK',
          'error_code: N8N_MEMBERSHIP_DENIED',
          'blocked_by: MEMBERSHIP_CAPABILITY_DENIED',
        ],
      },
    ],
  },
};

