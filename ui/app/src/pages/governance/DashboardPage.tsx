import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import type { ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import { useGovernanceCanvasSlot } from '../../components/governance/GovernanceCanvasSlot';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import { useGovernancePromptQuerySync } from '../../features/governanceInteraction/useGovernancePromptQuerySync';
import type { IntentState } from '../../features/governanceInteraction/interactionDecision';
import styles from './DashboardPage.module.css';

type KpiTone = 'neutral' | 'danger' | 'warning' | 'success' | 'active';
type GateState = 'pass' | 'warn' | 'fail';
type QueueState = 'Blocked' | 'Fix Required' | 'In Review' | 'Ready for Permit';
interface GateHealthItem {
  gate: string;
  blocked: number;
  affectedAssets: number;
  passRate: string;
  state: GateState;
}

interface QueueItem {
  asset: string;
  revision: string;
  status: QueueState;
  gate: string;
  nextAction: string;
  owner: string;
  updatedAt: string;
}

const gateHealth: GateHealthItem[] = [
  { gate: 'Gate 1', blocked: 0, affectedAssets: 32, passRate: '100%', state: 'pass' },
  { gate: 'Gate 2', blocked: 1, affectedAssets: 14, passRate: '91%', state: 'warn' },
  { gate: 'Gate 3', blocked: 2, affectedAssets: 9, passRate: '83%', state: 'warn' },
  { gate: 'Gate 4', blocked: 4, affectedAssets: 7, passRate: '71%', state: 'fail' },
  { gate: 'Gate 5', blocked: 1, affectedAssets: 5, passRate: '88%', state: 'warn' },
  { gate: 'Gate 6', blocked: 0, affectedAssets: 3, passRate: '97%', state: 'pass' },
  { gate: 'Gate 7', blocked: 0, affectedAssets: 3, passRate: '100%', state: 'pass' },
  { gate: 'Gate 8', blocked: 0, affectedAssets: 2, passRate: '100%', state: 'pass' },
];

const priorityQueue: QueueItem[] = [
  {
    asset: 'Payment Agent Skill',
    revision: 'R-014',
    status: 'Ready for Permit',
    gate: 'Gate 8',
    nextAction: 'Issue Permit',
    owner: 'Compliance-01',
    updatedAt: '12 min ago',
  },
  {
    asset: 'Invoice Reconciliation Flow',
    revision: 'R-032',
    status: 'Blocked',
    gate: 'Gate 4',
    nextAction: 'Review Gaps',
    owner: 'vs--cc1',
    updatedAt: '28 min ago',
  },
  {
    asset: 'Support Escalation Agent',
    revision: 'R-011',
    status: 'Fix Required',
    gate: 'Gate 3',
    nextAction: 'Open Audit Detail',
    owner: 'Antigravity-1',
    updatedAt: '1 h ago',
  },
];

const gapHotspots = [
  'Gate 4 boundary verification failures remain the most common blocker.',
  'Revision drift is the leading invalidation pattern for recently re-audited assets.',
  'Restricted evidence requests increased for permit-ready assets after policy refresh.',
];

const PAGE_COPY = {
  zh: {
    heroEyebrow: '治理概述',
    heroTitle: '把首页输入带进正确的工作流。',
    heroSubtitle: '这里不是治理全景陈列页，而是首页之后的承接页：先确认系统理解了什么，再决定进入哪条路径。',
    openQueue: '打开工作队列',
    viewPermitEvents: '查看许可事件',
    consoleEyebrow: '治理控制台',
    consoleTitle: '描述你希望系统帮助你进行管理的行动。',
    consoleMeta: '先输入，再自信地路由',
    promptBadge: '继续对话',
    promptHelp: '在这里继续补充需求、追问当前状态，或要求系统带你进入下一步。',
    promptPlaceholder: '继续在这里和系统对话。例如：审查这个外部 skill 是否可以安装，或者检查 R-014 是否可以申请 Permit。',
    intentVetting: '导入外部 Skill',
    intentAudit: '审查 Revision',
    intentPermit: '申请 Permit',
    submit: '提交',
    newline: '换行',
    confirmInput: '确认输入',
    consoleHint: '这不是聊天页，而是一个受控入口。先确认意图，再进入对应治理流程。',
    homeHistoryTitle: '首页已确认记录',
    homeHistorySubtitle: '从首页进入时的最近输入',
    needsConfirmation: '需要进一步确认',
    confirmedInput: '已确认输入',
    waitingInput: '等待输入',
    waitingInputDesc: '输入一句需求后，这里会出现最适合的治理路径和下一步动作。',
    bridgeEyebrow: '意图承接',
    bridgeTitle: '系统先复述你的输入，再推荐下一步。',
    bridgeSubtitle: '第一次来到这里时，你不需要理解所有治理板块，只需要确认系统是否理解了你的需求。',
    bridgeReasonLabel: '系统为何这样判断',
    bridgeReasonUnknown: '当前输入还不足以安全分流，因此系统只记录输入并要求补充上下文。',
    bridgePrimary: '推荐下一步',
    bridgeSecondary: '其它可选路径',
    bridgeClarify: '先补充说明',
    bridgeClarifyHelp: '请说明这是外部 Skill、当前 Revision，还是 Permit 放行需求。',
    bridgeDetailsSummary: '查看治理细节',
    bridgeDetailsHint: '只有在需要理解系统压力、证据覆盖和近期 Permit 事件时，再展开这部分。',
    recommended: '推荐',
    focusBlockedLabel: '当前阻断',
    focusBlockedHelper: '需要立即介入的资产',
    focusBlockedAction: '审查阻断资产',
    focusFixLabel: '下一步修复',
    focusFixHelper: '仍然阻止放行的可修复缺口',
    focusFixAction: '打开修复队列',
    focusPermitLabel: '可申请许可',
    focusPermitHelper: '已满足正式放行凭证条件',
    focusPermitAction: '签发 Permit',
    doThisNextEyebrow: '先做这个',
    doThisNextTitle: '今天的优先队列',
    doThisNextMeta: '3 个事项待处理',
    owner: 'Owner',
    updated: 'Updated',
    systemPressureEyebrow: '系统压力',
    systemPressureTitle: '当前审计拥塞集中在哪里',
    systemPressureMeta: '最拥塞：Gate 4',
    affectedAssets: '受影响资产',
    blocked: '阻断',
    passRate: '通过率',
    evidenceCoverageEyebrow: '证据覆盖',
    evidenceCoverageTitle: '当前决策依据的完整度',
    coverageSufficient: '充分',
    coverageSummaryOnly: '仅摘要',
    coverageWeak: '薄弱',
    coverageSufficientHelper: '证据包足以支撑最终裁决',
    coverageSummaryOnlyHelper: '更多细节需要更高权限查看',
    coverageWeakHelper: '证据存在，但仍需修复',
    gapHotspotsEyebrow: '缺口热点',
    gapHotspotsTitle: '当前修复工作主要集中在哪些地方',
    permitEventsEyebrow: '许可事件',
    permitEventsTitle: '最近的正式放行凭证活动',
    revisionWatchEyebrow: '修订监视',
    revisionWatchTitle: '哪些变化会使审计或 Permit 假设失效',
    operatorGuidanceEyebrow: '操作员说明',
    operatorGuidanceTitle: '如何使用本页',
    guide1: '先看优先队列，而不是先看完整 Gate 矩阵。',
    guide2: 'Gate 压力只用来判断失败正在集中在哪里。',
    guide3: '只有条目标记为可申请 Permit 时，才进入正式签发。',
    queueStatus: {
      Blocked: 'Blocked',
      'Fix Required': 'Fix Required',
      'In Review': 'In Review',
      'Ready for Permit': 'Ready for Permit',
    },
    permitState: {
      Issued: 'Issued',
      Revoked: 'Revoked',
      Expired: 'Expired',
    },
    queueData: [
      { asset: '支付代理 Skill', revision: 'R-014', gate: 'Gate 8', nextAction: '签发 Permit', owner: 'Compliance-01', updatedAt: '12 分钟前' },
      { asset: '发票核对流程', revision: 'R-032', gate: 'Gate 4', nextAction: '审查缺口', owner: 'vs--cc1', updatedAt: '28 分钟前' },
      { asset: '客服升级代理', revision: 'R-011', gate: 'Gate 3', nextAction: '打开审计详情', owner: 'Antigravity-1', updatedAt: '1 小时前' },
    ],
    permitData: [
      { asset: '支付代理 Skill', signedBy: 'Compliance-01', time: '09:30 CST' },
      { asset: '风险分流工作流', signedBy: 'Compliance-02', time: '昨天' },
      { asset: '合作方接入代理', signedBy: 'Compliance-01', time: '2 天前' },
    ],
    watchData: [
      { asset: '理赔路由器', revision: 'R-022', impact: '最新 Permit 之后 Rulepack 已变化', action: '需要重新审计' },
      { asset: '欺诈信号 Skill', revision: 'R-006', impact: '关联合约出现 hash 漂移', action: '暂停 Permit 签发' },
      { asset: '账单异常代理', revision: 'R-019', impact: '新修订等待证据刷新', action: '审查证据覆盖' },
    ],
    gapHotspots: [
      'Gate 4 边界校验失败仍是最常见阻断点。',
      'Revision 漂移是最近重审资产失效的主要模式。',
      '策略刷新后，Permit 就绪资产的 restricted evidence 请求上升。',
    ],
  },
  en: {
    heroEyebrow: 'Governance Overview',
    heroTitle: 'Carry homepage intent into the right governed workflow.',
    heroSubtitle: 'This is not a governance panorama. It is the bridge after Home: first confirm what the system understood, then decide which path to enter.',
    openQueue: 'Open work queue',
    viewPermitEvents: 'View permit events',
    consoleEyebrow: 'Govern Console',
    consoleTitle: 'Describe the action you want the system to help you govern.',
    consoleMeta: 'Input first, then route with confidence',
    promptBadge: 'Continue',
    promptHelp: 'Keep refining the request here, ask about current status, or ask the system to guide you into the next step.',
    promptPlaceholder: 'Continue the conversation here. For example: vet whether this external skill can be installed, or check whether R-014 is permit-ready.',
    intentVetting: 'Import External Skill',
    intentAudit: 'Review Revision',
    intentPermit: 'Request Permit',
    submit: 'Submit',
    newline: 'New line',
    confirmInput: 'Confirm Input',
    consoleHint: 'This is not a chat page. It is a governed entry point: confirm intent first, then enter the right path.',
    homeHistoryTitle: 'Confirmed inputs from Home',
    homeHistorySubtitle: 'Most recent entries captured on the homepage',
    needsConfirmation: 'Needs clarification',
    confirmedInput: 'Confirmed Input',
    waitingInput: 'Waiting for input',
    waitingInputDesc: 'After you enter a request, the best governed path and next action will appear here.',
    bridgeEyebrow: 'Intent bridge',
    bridgeTitle: 'The system should restate your intent before it routes you.',
    bridgeSubtitle: 'When you arrive here for the first time, you should not need to understand every governance module. You only need to confirm whether the system understood the request.',
    bridgeReasonLabel: 'Why the system is leaning this way',
    bridgeReasonUnknown: 'The current input is not strong enough to route safely, so the system records it and asks for more context.',
    bridgePrimary: 'Recommended next step',
    bridgeSecondary: 'Other possible paths',
    bridgeClarify: 'Clarify first',
    bridgeClarifyHelp: 'Tell the system whether this is an external skill, a current revision, or a permit request.',
    bridgeDetailsSummary: 'View governance details',
    bridgeDetailsHint: 'Open this only when you need pressure, evidence, and permit event context.',
    recommended: 'Recommended',
    focusBlockedLabel: 'Blocked now',
    focusBlockedHelper: 'assets that need immediate intervention',
    focusBlockedAction: 'Review blocked assets',
    focusFixLabel: 'Fix next',
    focusFixHelper: 'repairable gaps still prevent release',
    focusFixAction: 'Open fix queue',
    focusPermitLabel: 'Ready for permit',
    focusPermitHelper: 'eligible for formal release credential',
    focusPermitAction: 'Issue permit',
    doThisNextEyebrow: 'Do This Next',
    doThisNextTitle: 'Priority queue for today.',
    doThisNextMeta: '3 items need attention',
    owner: 'Owner',
    updated: 'Updated',
    systemPressureEyebrow: 'System pressure',
    systemPressureTitle: 'Where audit congestion is building.',
    systemPressureMeta: 'Most congested: Gate 4',
    affectedAssets: 'affected assets',
    blocked: 'blocked',
    passRate: 'pass rate',
    evidenceCoverageEyebrow: 'Evidence coverage',
    evidenceCoverageTitle: 'How complete the decision basis currently is.',
    coverageSufficient: 'Sufficient',
    coverageSummaryOnly: 'Summary Only',
    coverageWeak: 'Weak Coverage',
    coverageSufficientHelper: 'evidence packages support final adjudication',
    coverageSummaryOnlyHelper: 'restricted detail requires elevated review',
    coverageWeakHelper: 'evidence exists but remediation still required',
    gapHotspotsEyebrow: 'Gap hotspots',
    gapHotspotsTitle: 'Where repair effort is currently concentrated.',
    permitEventsEyebrow: 'Permit events',
    permitEventsTitle: 'Recent release credential activity.',
    revisionWatchEyebrow: 'Revision watch',
    revisionWatchTitle: 'Changes that can invalidate audit or permit assumptions.',
    operatorGuidanceEyebrow: 'Operator guidance',
    operatorGuidanceTitle: 'How to use this page.',
    guide1: 'Start with the priority queue, not the full gate matrix.',
    guide2: 'Use gate pressure only to understand where failures are clustering.',
    guide3: 'Issue permits only after an item is marked ready for permit.',
    queueStatus: {
      Blocked: 'Blocked',
      'Fix Required': 'Fix Required',
      'In Review': 'In Review',
      'Ready for Permit': 'Ready for Permit',
    },
    permitState: {
      Issued: 'Issued',
      Revoked: 'Revoked',
      Expired: 'Expired',
    },
    queueData: [
      { asset: 'Payment Agent Skill', revision: 'R-014', gate: 'Gate 8', nextAction: 'Issue Permit', owner: 'Compliance-01', updatedAt: '12 min ago' },
      { asset: 'Invoice Reconciliation Flow', revision: 'R-032', gate: 'Gate 4', nextAction: 'Review Gaps', owner: 'vs--cc1', updatedAt: '28 min ago' },
      { asset: 'Support Escalation Agent', revision: 'R-011', gate: 'Gate 3', nextAction: 'Open Audit Detail', owner: 'Antigravity-1', updatedAt: '1 h ago' },
    ],
    permitData: [
      { asset: 'Payment Agent Skill', signedBy: 'Compliance-01', time: '09:30 CST' },
      { asset: 'Risk Triage Workflow', signedBy: 'Compliance-02', time: 'Yesterday' },
      { asset: 'Partner Intake Agent', signedBy: 'Compliance-01', time: '2 days ago' },
    ],
    watchData: [
      { asset: 'Claims Router', revision: 'R-022', impact: 'Rulepack changed after latest permit', action: 'Re-audit required' },
      { asset: 'Fraud Signals Skill', revision: 'R-006', impact: 'Hash drift detected in linked contract', action: 'Hold permit issuance' },
      { asset: 'Billing Exception Agent', revision: 'R-019', impact: 'New revision awaiting evidence refresh', action: 'Review evidence coverage' },
    ],
    gapHotspots,
  },
} as const;

type IntentKey = Exclude<IntentState, 'unknown'>;

const FALLBACK_INTENT_TITLE: Record<'zh' | 'en', Record<IntentKey, string>> = {
  zh: {
    vetting: '外部 Skill 审查',
    audit: 'Revision 审核',
    permit: 'Permit 放行',
  },
  en: {
    vetting: 'External Skill Vetting',
    audit: 'Revision Audit',
    permit: 'Permit Decision',
  },
};

const getKpiToneClass = (tone: KpiTone): string => {
  switch (tone) {
    case 'danger':
      return styles.kpiDanger;
    case 'warning':
      return styles.kpiWarning;
    case 'success':
      return styles.kpiSuccess;
    case 'active':
      return styles.kpiActive;
    default:
      return styles.kpiNeutral;
  }
};

const getGateStateClass = (state: GateState): string => {
  switch (state) {
    case 'fail':
      return styles.gateFail;
    case 'warn':
      return styles.gateWarn;
    default:
      return styles.gatePass;
  }
};

const getQueueStateClass = (state: QueueState): string => {
  switch (state) {
    case 'Blocked':
      return styles.statusBlocked;
    case 'Fix Required':
      return styles.statusFix;
    case 'Ready for Permit':
      return styles.statusPermit;
    default:
      return styles.statusReview;
  }
};

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const {
    draft,
    setDraft,
    draftIntentHint,
    setDraftIntentHint,
    submitDraft,
    activeDecision,
    latestTurn,
    latestTurns,
    isTyping,
  } = useGovernanceInteraction();
  useGovernancePromptQuerySync();
  const copy = PAGE_COPY[language];
  const currentTurn = isTyping ? draft.trim() : latestTurn?.userInput || '';
  const historyItems = useMemo<ContextCanvasHistoryItem[]>(
    () =>
      latestTurns.map((turn) => ({
        id: turn.id,
        input: turn.userInput,
        state:
          turn.intent === 'unknown'
            ? copy.needsConfirmation
            : turn.decision.canvasPayload?.primaryTitle ??
              FALLBACK_INTENT_TITLE[language][turn.intent as IntentKey],
      })),
    [copy.needsConfirmation, language, latestTurns],
  );
  const quickActions = useMemo<ComposerAction[]>(
    () => [
      { label: copy.intentVetting, prompt: copy.promptPlaceholder, icon: '↘', intentHint: 'vetting' },
      { label: copy.intentAudit, prompt: language === 'zh' ? '检查当前 Revision 是否已经准备好申请许可' : 'Check whether the current revision is ready for permit review', icon: '◎', intentHint: 'audit' },
      { label: copy.intentPermit, prompt: language === 'zh' ? '为这个 Skill 申请 Permit 放行' : 'Request permit release for this skill', icon: '◆', intentHint: 'permit' },
    ],
    [copy.intentAudit, copy.intentPermit, copy.intentVetting, copy.promptPlaceholder, language],
  );

  const slotConfig = useMemo(
    () => ({
      variant: 'workspace' as const,
      decision: activeDecision,
      confirmedValue: currentTurn || undefined,
      showHistory: Boolean(latestTurns.length > 0),
      history: {
        title: copy.homeHistoryTitle,
        subtitle: copy.homeHistorySubtitle,
        items: historyItems,
      },
      consoleHeader: {
        eyebrow: copy.consoleEyebrow,
        title: copy.consoleTitle,
        meta: copy.consoleMeta,
      },
      consoleHint: copy.consoleHint,
      canvasHeader: {
        eyebrow: copy.bridgeEyebrow,
        title: copy.bridgeTitle,
        status:
          activeDecision.canvasPayload?.status ??
          (activeDecision.intent === 'unknown' ? copy.needsConfirmation : undefined),
      },
      composer: {
        value: draft,
        onChange: setDraft,
        onSubmit: () => {
          submitDraft({ intentHint: draftIntentHint });
        },
        placeholder: copy.promptPlaceholder,
        submitLabel: copy.confirmInput,
        addAttachmentLabel: language === 'zh' ? '添加附件' : 'Add attachment',
        imageActionLabel: language === 'zh' ? '图片' : 'Image',
        fileActionLabel: language === 'zh' ? '文件' : 'File',
        enterKeyLabel: 'Enter',
        enterLabel: copy.submit,
        shiftEnterKeyLabel: 'Shift+Enter',
        newlineLabel: copy.newline,
        separatorLabel: '·',
        imageAttachedLabel: language === 'zh' ? '已附加图片' : 'Image attached',
        fileAttachedLabel: language === 'zh' ? '已附加文件' : 'File attached',
        headerBadge: copy.promptBadge,
        headerText: copy.promptHelp,
        quickActions,
        onQuickActionSelect: (action: ComposerAction) => {
          setDraft(action.prompt);
          setDraftIntentHint(action.intentHint ?? 'unknown');
        },
        intentTabs: [
          { key: 'vetting' as const, label: copy.intentVetting },
          { key: 'audit' as const, label: copy.intentAudit },
          { key: 'permit' as const, label: copy.intentPermit },
        ],
        selectedIntent: draftIntentHint,
        onIntentSelect: setDraftIntentHint,
      },
      onPrimaryAction: (decision: typeof activeDecision) => {
        if (decision.routeTarget && currentTurn) {
          navigate(`${decision.routeTarget}?prompt=${encodeURIComponent(currentTurn)}`);
        }
      },
      onAlternativeSelect: (intent: 'vetting' | 'audit' | 'permit') => setDraftIntentHint(intent),
    }),
    [
      activeDecision,
      copy.bridgeEyebrow,
      copy.bridgeTitle,
      copy.confirmInput,
      copy.consoleEyebrow,
      copy.consoleHint,
      copy.consoleMeta,
      copy.consoleTitle,
      copy.homeHistorySubtitle,
      copy.homeHistoryTitle,
      copy.intentAudit,
      copy.intentPermit,
      copy.intentVetting,
      copy.newline,
      copy.promptBadge,
      copy.promptHelp,
      copy.promptPlaceholder,
      copy.submit,
      currentTurn,
      draft,
      draftIntentHint,
      historyItems,
      language,
      latestTurns.length,
      navigate,
      quickActions,
      setDraft,
      setDraftIntentHint,
      submitDraft,
    ],
  );

  useGovernanceCanvasSlot(slotConfig);

  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroMain}>
          <p className={styles.eyebrow}>{copy.heroEyebrow}</p>
          <h1 className={styles.title}>{copy.heroTitle}</h1>
          <p className={styles.subtitle}>
            {copy.heroSubtitle}
          </p>
        </div>
        <div className={styles.heroActions}>
          <button className={styles.primaryAction}>{copy.openQueue}</button>
          <button className={styles.secondaryAction}>{copy.viewPermitEvents}</button>
        </div>
      </section>
      <details className={styles.detailsPanel}>
        <summary className={styles.detailsSummary}>
          <div>
            <strong>{copy.bridgeDetailsSummary}</strong>
            <span>{copy.bridgeDetailsHint}</span>
          </div>
        </summary>

        <div className={styles.detailsContent}>
          <section className={styles.focusRow}>
            {[
              { label: copy.focusBlockedLabel, value: '4', helper: copy.focusBlockedHelper, action: copy.focusBlockedAction, tone: 'danger' as KpiTone },
              { label: copy.focusFixLabel, value: '11', helper: copy.focusFixHelper, action: copy.focusFixAction, tone: 'warning' as KpiTone },
              { label: copy.focusPermitLabel, value: '6', helper: copy.focusPermitHelper, action: copy.focusPermitAction, tone: 'success' as KpiTone },
            ].map((card) => (
              <article key={card.label} className={`${styles.kpiCard} ${getKpiToneClass(card.tone)}`}>
                <span className={styles.kpiLabel}>{card.label}</span>
                <strong className={styles.kpiValue}>{card.value}</strong>
                <p className={styles.kpiHelper}>{card.helper}</p>
                <button className={styles.focusAction}>{card.action}</button>
              </article>
            ))}
          </section>

          <section className={styles.primaryQueueSection}>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.panelEyebrow}>{copy.doThisNextEyebrow}</p>
                  <h2 className={styles.panelTitle}>{copy.doThisNextTitle}</h2>
                </div>
                <span className={styles.panelMeta}>{copy.doThisNextMeta}</span>
              </div>
              <div className={styles.queueList}>
                {copy.queueData.map((item, index) => (
                  <div key={`${item.asset}-${item.revision}`} className={styles.queueCard}>
                    <div className={styles.queueTop}>
                      <div>
                        <strong>{item.asset}</strong>
                        <p>{item.revision} · {item.gate}</p>
                      </div>
                      <span className={`${styles.statusPill} ${getQueueStateClass(priorityQueue[index].status)}`}>{copy.queueStatus[priorityQueue[index].status]}</span>
                    </div>
                    <div className={styles.queueMeta}>
                      <span>{copy.owner}: {item.owner}</span>
                      <span>{copy.updated}: {item.updatedAt}</span>
                    </div>
                    <button className={styles.queueAction}>{item.nextAction}</button>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className={styles.supportingGrid}>
            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.panelEyebrow}>{copy.systemPressureEyebrow}</p>
                  <h2 className={styles.panelTitle}>{copy.systemPressureTitle}</h2>
                </div>
                <span className={styles.panelMeta}>{copy.systemPressureMeta}</span>
              </div>
              <div className={styles.gateList}>
                {gateHealth.map((item) => (
                  <div key={item.gate} className={styles.gateRow}>
                    <div className={styles.gateMain}>
                      <span className={`${styles.gateDot} ${getGateStateClass(item.state)}`} />
                      <div>
                        <strong>{item.gate}</strong>
                        <p>{item.affectedAssets} {copy.affectedAssets}</p>
                      </div>
                    </div>
                    <div className={styles.gateStats}>
                      <span>{item.passRate} {copy.passRate}</span>
                      <span>{item.blocked} {copy.blocked}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className={styles.panel}>
              <div className={styles.panelHeader}>
                <div>
                  <p className={styles.panelEyebrow}>{copy.evidenceCoverageEyebrow}</p>
                  <h2 className={styles.panelTitle}>{copy.evidenceCoverageTitle}</h2>
                </div>
              </div>
              <div className={styles.coverageList}>
                {[
                  { label: copy.coverageSufficient, value: '27', helper: copy.coverageSufficientHelper },
                  { label: copy.coverageSummaryOnly, value: '8', helper: copy.coverageSummaryOnlyHelper },
                  { label: copy.coverageWeak, value: '5', helper: copy.coverageWeakHelper },
                ].map((item) => (
                  <div key={item.label} className={styles.coverageCard}>
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                    <p>{item.helper}</p>
                  </div>
                ))}
              </div>
            </article>
          </section>
        </div>
      </details>
    </main>
  );
};

export default DashboardPage;
