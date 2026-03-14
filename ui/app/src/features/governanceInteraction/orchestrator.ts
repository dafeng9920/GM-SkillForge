export type IntentKey = 'vetting' | 'audit' | 'permit';
export type IntentState = IntentKey | 'unknown';
export type CanvasState = 'home' | 'clarify' | 'vetting' | 'audit' | 'permit' | 'overview';
export type DecisionConfidence = 'high' | 'low';

export interface DecisionNextAction {
  id: string;
  label: string;
  intent?: IntentKey;
  route_target?: string;
}

export interface InteractionDecision {
  intent: IntentState;
  canvas: CanvasState;
  confidence: DecisionConfidence;
  requiresClarification: boolean;
  routeTarget: string | null;
  reason?: string;
  nextActions?: DecisionNextAction[];
  profile?: string | null;
  capabilitySegments?: string[];
}

export const INTENT_ROUTE_MAP: Record<IntentKey, string> = {
  vetting: '/intake/vetting',
  audit: '/audit/detail',
  permit: '/permit',
};

export const inferIntent = (value: string): IntentState => {
  const normalized = value.toLowerCase();

  if (!/[a-z\u4e00-\u9fa5]/i.test(normalized)) {
    return 'unknown';
  }

  if (
    normalized.includes('外部') ||
    normalized.includes('import') ||
    normalized.includes('repo') ||
    normalized.includes('package') ||
    normalized.includes('skill') ||
    normalized.includes('install') ||
    normalized.includes('安装') ||
    normalized.includes('vet')
  ) {
    return 'vetting';
  }

  if (
    normalized.includes('permit') ||
    normalized.includes('release') ||
    normalized.includes('publish') ||
    normalized.includes('sign') ||
    normalized.includes('放行') ||
    normalized.includes('许可')
  ) {
    return 'permit';
  }

  if (
    normalized.includes('revision') ||
    normalized.includes('audit') ||
    normalized.includes('evidence') ||
    normalized.includes('gap') ||
    normalized.includes('审计') ||
    normalized.includes('修订') ||
    normalized.includes('证据') ||
    normalized.includes('缺口') ||
    normalized.includes('裁决')
  ) {
    return 'audit';
  }

  return 'unknown';
};

export const resolveCanvas = (intent: IntentState): CanvasState => {
  switch (intent) {
    case 'vetting':
      return 'vetting';
    case 'audit':
      return 'audit';
    case 'permit':
      return 'permit';
    default:
      return 'clarify';
  }
};

export const resolveInteractionDecision = (
  value: string,
  intentHint: IntentState = 'unknown',
): InteractionDecision => {
  const intent = intentHint !== 'unknown' ? intentHint : inferIntent(value);
  const canvas = resolveCanvas(intent);
  const requiresClarification = intent === 'unknown';

  return {
    intent,
    canvas,
    confidence: requiresClarification ? 'low' : 'high',
    requiresClarification,
    routeTarget: requiresClarification ? null : INTENT_ROUTE_MAP[intent],
    reason: requiresClarification
      ? 'Input recorded, but more context is required before the governed flow can be selected safely.'
      : intent === 'vetting'
        ? 'Detected external asset / pre-install governance language. Route into governed vetting intake.'
        : intent === 'audit'
          ? 'Detected revision / evidence / gap review language. Route into audit detail.'
          : 'Detected release / permit language. Route into formal permit handling.',
    nextActions: requiresClarification
      ? [
          { id: 'clarify-vetting', label: 'Clarify as external skill intake', intent: 'vetting' },
          { id: 'clarify-audit', label: 'Clarify as revision audit', intent: 'audit' },
          { id: 'clarify-permit', label: 'Clarify as permit request', intent: 'permit' },
        ]
      : [
          {
            id: `open-${intent}`,
            label:
              intent === 'vetting'
                ? 'Open vetting intake'
                : intent === 'audit'
                  ? 'Open audit detail'
                  : 'Open permit page',
            route_target: INTENT_ROUTE_MAP[intent],
          },
        ],
    profile:
      intent === 'vetting'
        ? 'external_skill_vetting'
        : intent === 'audit'
          ? 'revision_audit'
          : intent === 'permit'
            ? 'permit_release'
            : null,
    capabilitySegments:
      intent === 'vetting'
        ? [
            'source_trust_scan',
            'code_redline_scan',
            'permission_capability_fit_review',
            'risk_adjudication',
            'install_gate',
          ]
        : intent === 'audit'
          ? ['evidence_review', 'gap_adjudication', 'decision_explanation']
          : intent === 'permit'
            ? ['permit_binding', 'scope_conditions', 'release_gate']
            : [],
  };
};
