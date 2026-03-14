import type { CanvasState, InteractionDecision, IntentState } from './orchestrator';

export interface CanvasRouteDescriptor {
  eyebrow: string;
  title: string;
  summary: string;
  status: string;
  primaryAction: string;
  secondaryAction: string;
  recommendation: string;
}

type Language = 'zh' | 'en';
export type CanvasIntentKey = Exclude<IntentState, 'unknown'>;

export interface ContextCanvasModel {
  canvas: Extract<CanvasState, 'clarify' | 'vetting' | 'audit' | 'permit'>;
  profileLabel?: string;
  profileValue?: string;
  summary: string;
  status: string;
  confirmedLabel: string;
  emptyTitle: string;
  emptyDescription: string;
  reasonLabel: string;
  reasonText: string;
  primaryLabel: string;
  primaryTitle: string;
  primaryDescription: string;
  primaryActionLabel: string;
  secondaryActionLabel?: string;
  capabilityLabel?: string;
  capabilitySegments?: string[];
  detailItems?: Array<{ label: string; value: string }>;
  alternativesLabel: string;
  alternatives: Array<{
    key: CanvasIntentKey;
    title: string;
    eyebrow: string;
    active: boolean;
  }>;
}

const ROUTE_DESCRIPTORS: Record<Language, Record<CanvasIntentKey, CanvasRouteDescriptor>> = {
  zh: {
    vetting: {
      eyebrow: '摄入路径',
      title: '外部 Skill 审查',
      summary: '当请求描述外部 skill、包、仓库或不受信任的外部资产时，使用这条路径。',
      status: '需要入口裁决',
      primaryAction: '打开审查入口',
      secondaryAction: '查看示例报告',
      recommendation: '最适合在安装或发布前处理外部 Skill。',
    },
    audit: {
      eyebrow: '审计路径',
      title: 'Revision 审核',
      summary: '当请求要求当前版本检查、证据审查、缺口分析或解释被阻止的决定时，使用此功能。',
      status: '准备接受审计审查',
      primaryAction: '打开审计详情',
      secondaryAction: '审查被冻结资产',
      recommendation: '最适合用于当前修订、填补空白和裁决审查。',
    },
    permit: {
      eyebrow: '发布路径',
      title: 'Permit 放行',
      summary: '当请求涉及放行、签发、失效或进入正式 Permit 审批时，使用这条路径。',
      status: '准备接受 Permit 审查',
      primaryAction: '打开 Permit 决策',
      secondaryAction: '打开关联报告',
      recommendation: '最适合处理放行决策和 Permit 绑定动作。',
    },
  },
  en: {
    vetting: {
      eyebrow: 'Intake path',
      title: 'External Skill Vetting',
      summary: 'Use this when the request describes an imported skill, package, repo or untrusted external asset.',
      status: 'Needs intake adjudication',
      primaryAction: 'Open vetting intake',
      secondaryAction: 'View sample report',
      recommendation: 'Best for external skills before install or release.',
    },
    audit: {
      eyebrow: 'Audit path',
      title: 'Revision Audit',
      summary: 'Use this when the request asks for a current revision check, evidence review, gap analysis or blocked decision explanation.',
      status: 'Ready for audit review',
      primaryAction: 'Open audit detail',
      secondaryAction: 'Review blocked assets',
      recommendation: 'Best for current revisions, gaps, and adjudication review.',
    },
    permit: {
      eyebrow: 'Release path',
      title: 'Permit Decision',
      summary: 'Use this when the request asks whether a revision can be released, signed, invalidated or moved into permit issuance.',
      status: 'Ready for permit review',
      primaryAction: 'Open permit decision',
      secondaryAction: 'Open linked report',
      recommendation: 'Best for release decisions and permit-bound actions.',
    },
  },
};

const INTENT_REASONS: Record<Language, Record<IntentState, string>> = {
  zh: {
    unknown: '当前输入还不足以安全分流，因此系统只记录输入并要求补充上下文。',
    vetting: '检测到外部来源、导入、安装前判断或不受信任资产相关表达，因此优先进入入口审查路径。',
    audit: '检测到修订、证据、缺口或裁决相关表达，因此优先进入审计解释路径。',
    permit: '检测到 Permit、放行、签发或发布约束相关表达，因此优先进入正式放行路径。',
  },
  en: {
    unknown: 'The current input is not strong enough to route safely, so the system records it and asks for more context.',
    vetting: 'The request mentions external source, import, install judgment, or untrusted assets, so the intake vetting path is prioritized.',
    audit: 'The request mentions revision, evidence, gaps, or adjudication, so the audit explanation path is prioritized.',
    permit: 'The request mentions permit, release, issuance, or release constraints, so the formal permit path is prioritized.',
  },
};

const CONTEXT_COPY = {
  zh: {
    summary: '系统先确认你的输入，再给出最适合的治理承接画布。',
    confirmedLabel: '已确认输入',
    emptyTitle: '等待输入',
    emptyDescription: '输入一句需求后，这里会出现最适合的治理路径和下一步动作。',
    reasonLabel: '系统为何这样判断',
    primaryLabel: '推荐下一步',
    alternativesLabel: '其它可选路径',
    clarifyTitle: '先补充说明',
    clarifyDescription: '请补充这是外部 Skill、当前 Revision，还是 Permit 放行需求。',
    clarifyAction: '继续补充说明',
    clarifyStatus: '需要进一步确认',
  },
  en: {
    summary: 'The system first confirms your input, then presents the most suitable governed canvas.',
    confirmedLabel: 'Confirmed Input',
    emptyTitle: 'Waiting for input',
    emptyDescription: 'After you enter a request, the best governed path and next action will appear here.',
    reasonLabel: 'Why the system is leaning this way',
    primaryLabel: 'Recommended next step',
    alternativesLabel: 'Other possible paths',
    clarifyTitle: 'Clarify first',
    clarifyDescription: 'Clarify whether this is an external skill, a current revision, or a permit release request.',
    clarifyAction: 'Continue clarifying',
    clarifyStatus: 'Clarification required',
  },
} as const;

const getOrderedAlternatives = (intent: IntentState): CanvasIntentKey[] => {
  const all: CanvasIntentKey[] = ['vetting', 'audit', 'permit'];

  if (intent === 'unknown') {
    return all;
  }

  return [intent, ...all.filter((item) => item !== intent)];
};

export const getCanvasRouteDescriptors = (language: Language) => ROUTE_DESCRIPTORS[language];

export const getCanvasRouteDescriptor = (
  language: Language,
  intent: CanvasIntentKey,
): CanvasRouteDescriptor => ROUTE_DESCRIPTORS[language][intent];

export const getCanvasReason = (language: Language, intent: IntentState): string =>
  INTENT_REASONS[language][intent];

export const buildContextCanvasModel = (
  language: Language,
  decision: InteractionDecision,
): ContextCanvasModel => {
  const copy = CONTEXT_COPY[language];
  const alternatives = getOrderedAlternatives(decision.intent).map((key) => ({
    key,
    title: ROUTE_DESCRIPTORS[language][key].title,
    eyebrow: ROUTE_DESCRIPTORS[language][key].eyebrow,
    active: key === decision.intent,
  }));

  if (decision.intent === 'unknown') {
    return {
      canvas: 'clarify',
      profileLabel: decision.canvasPayload?.profileLabel,
      profileValue: decision.canvasPayload?.profileValue,
      summary: decision.canvasPayload?.summary ?? copy.summary,
      status: decision.canvasPayload?.status ?? copy.clarifyStatus,
      confirmedLabel: copy.confirmedLabel,
      emptyTitle: copy.emptyTitle,
      emptyDescription: copy.emptyDescription,
      reasonLabel: decision.canvasPayload?.reasonLabel ?? copy.reasonLabel,
      reasonText: decision.canvasPayload?.reasonText ?? decision.reason ?? INTENT_REASONS[language].unknown,
      primaryLabel: decision.canvasPayload?.primaryLabel ?? copy.primaryLabel,
      primaryTitle: decision.canvasPayload?.primaryTitle ?? copy.clarifyTitle,
      primaryDescription: decision.canvasPayload?.primaryDescription ?? copy.clarifyDescription,
      primaryActionLabel:
        decision.canvasPayload?.primaryActionLabel ?? decision.nextActions?.[0]?.label ?? copy.clarifyAction,
      alternativesLabel: decision.canvasPayload?.alternativesLabel ?? copy.alternativesLabel,
      capabilityLabel: decision.canvasPayload?.capabilityLabel,
      capabilitySegments: decision.canvasPayload?.capabilitySegments ?? [],
      detailItems: decision.canvasPayload?.detailItems ?? [],
      alternatives,
    };
  }

  const descriptor = ROUTE_DESCRIPTORS[language][decision.intent];

  return {
    canvas: decision.canvas as Extract<CanvasState, 'clarify' | 'vetting' | 'audit' | 'permit'>,
    profileLabel: decision.canvasPayload?.profileLabel,
    profileValue: decision.canvasPayload?.profileValue ?? decision.profile ?? undefined,
    summary: decision.canvasPayload?.summary ?? copy.summary,
    status: decision.canvasPayload?.status ?? descriptor.status,
    confirmedLabel: copy.confirmedLabel,
    emptyTitle: copy.emptyTitle,
    emptyDescription: copy.emptyDescription,
    reasonLabel: decision.canvasPayload?.reasonLabel ?? copy.reasonLabel,
    reasonText: decision.canvasPayload?.reasonText ?? decision.reason ?? INTENT_REASONS[language][decision.intent],
    primaryLabel: decision.canvasPayload?.primaryLabel ?? copy.primaryLabel,
    primaryTitle: decision.canvasPayload?.primaryTitle ?? descriptor.title,
    primaryDescription: decision.canvasPayload?.primaryDescription ?? descriptor.summary,
    primaryActionLabel:
      decision.canvasPayload?.primaryActionLabel ?? decision.nextActions?.[0]?.label ?? descriptor.primaryAction,
    secondaryActionLabel:
      decision.canvasPayload?.secondaryActionLabel ?? decision.nextActions?.[1]?.label ?? descriptor.secondaryAction,
    capabilityLabel: decision.canvasPayload?.capabilityLabel ?? (language === 'zh' ? '后端能力段' : 'Capability segments'),
    capabilitySegments: decision.canvasPayload?.capabilitySegments ?? decision.capabilitySegments ?? [],
    detailItems: decision.canvasPayload?.detailItems ?? [],
    alternativesLabel: decision.canvasPayload?.alternativesLabel ?? copy.alternativesLabel,
    alternatives,
  };
};
