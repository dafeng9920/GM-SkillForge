export type IntentKey = 'vetting' | 'audit' | 'permit';
export type IntentState = IntentKey | 'unknown';
export type CanvasState = 'home' | 'clarify' | 'vetting' | 'audit' | 'permit' | 'overview';
export type DecisionConfidence = 'high' | 'low';
const VETTING_CAPABILITY_SEGMENTS = [
  'source_trust_scan',
  'code_redline_scan',
  'permission_capability_fit_review',
  'risk_adjudication',
  'install_gate',
] as const;

export interface DecisionNextAction {
  id: string;
  label: string;
  intent?: IntentKey;
  route_target?: string;
}

export interface DecisionCanvasPayload {
  profileLabel?: string;
  profileValue?: string;
  summary?: string;
  status?: string;
  reasonLabel?: string;
  reasonText?: string;
  primaryLabel?: string;
  primaryTitle?: string;
  primaryDescription?: string;
  primaryActionLabel?: string;
  secondaryActionLabel?: string;
  alternativesLabel?: string;
  capabilityLabel?: string;
  capabilitySegments?: string[];
  detailItems?: Array<{ label: string; value: string }>;
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
  canvasPayload?: DecisionCanvasPayload;
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
    canvasPayload: requiresClarification
      ? {
          summary: 'The system first confirms your input, then asks for the missing governance context.',
          status: 'Clarification required',
          reasonLabel: 'Why clarification is required',
          reasonText:
            'The current input is not strong enough to route safely, so the system records it and asks for more context.',
          primaryLabel: 'Clarify first',
          primaryTitle: 'Add missing governance context',
          primaryDescription:
            'Clarify whether this is an external skill, a current revision review, or a permit release request.',
          primaryActionLabel: 'Continue clarifying',
          alternativesLabel: 'Possible governed paths',
          capabilityLabel: 'Capability segments',
          capabilitySegments: [],
        }
      : {
          summary:
            intent === 'vetting'
              ? 'The system detected external intake language and prepared the governed vetting canvas.'
              : intent === 'audit'
                ? 'The system detected audit language and prepared the adjudication canvas.'
                : 'The system detected release language and prepared the permit decision canvas.',
          status:
            intent === 'vetting'
              ? 'Needs intake adjudication'
              : intent === 'audit'
                ? 'Ready for audit review'
                : 'Ready for permit review',
          reasonLabel: 'Why this canvas is active',
          reasonText:
            intent === 'vetting'
              ? 'External source, import, or pre-install intent was detected.'
              : intent === 'audit'
                ? 'Revision, evidence, or gap-review language was detected.'
                : 'Permit, release, or issuance language was detected.',
          primaryLabel: 'Recommended next step',
          primaryTitle:
            intent === 'vetting'
              ? 'External Skill Vetting'
              : intent === 'audit'
                ? 'Revision Audit'
                : 'Permit Decision',
          primaryDescription:
            intent === 'vetting'
              ? 'Use this canvas to review intake risk, redlines, and install gate readiness.'
              : intent === 'audit'
                ? 'Use this canvas to inspect evidence, gaps, blocked decisions, and adjudication context.'
                : 'Use this canvas to bind release scope, conditions, and formal permit issuance.',
          primaryActionLabel:
            intent === 'vetting'
              ? 'Open vetting intake'
              : intent === 'audit'
                ? 'Open audit detail'
                : 'Open permit page',
          secondaryActionLabel:
            intent === 'vetting'
              ? 'View sample report'
              : intent === 'audit'
                ? 'Review blocked assets'
                : 'Open linked audit',
          alternativesLabel: 'Other possible paths',
          capabilityLabel: 'Capability segments',
          capabilitySegments:
            intent === 'vetting'
              ? [...VETTING_CAPABILITY_SEGMENTS]
              : intent === 'audit'
                ? ['evidence_review', 'gap_adjudication', 'decision_explanation']
                : ['permit_binding', 'scope_conditions', 'release_gate'],
        },
  };
};
