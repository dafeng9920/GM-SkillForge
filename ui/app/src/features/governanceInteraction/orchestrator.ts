export type IntentKey = 'vetting' | 'audit' | 'permit';
export type IntentState = IntentKey | 'unknown';
export type CanvasState = 'home' | 'clarify' | 'vetting' | 'audit' | 'permit' | 'overview';
export type DecisionConfidence = 'high' | 'low';

export interface InteractionDecision {
  intent: IntentState;
  canvas: CanvasState;
  confidence: DecisionConfidence;
  requiresClarification: boolean;
  routeTarget: string | null;
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
  };
};
