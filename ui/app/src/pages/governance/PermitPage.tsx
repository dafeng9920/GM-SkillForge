import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import type { ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import { useGovernanceCanvasSlot } from '../../components/governance/GovernanceCanvasSlot';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { INTENT_ROUTE_MAP, useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import styles from './PermitPage.module.css';

type PermitStatus = 'Active' | 'Pending' | 'Revoked' | 'Expired' | 'Superseded';

interface LifecycleItem {
  label: string;
  time: string;
  actor?: string;
  state: 'done' | 'current' | 'future';
}

const permitData = {
  permitId: 'PMT-2026-0313-014',
  assetName: 'Payment Agent Skill',
  revision: 'R-014',
  status: 'Active' as PermitStatus,
  effectiveDate: '2026-03-13 09:30 CST',
  signedBy: 'Compliance-01',
  scope: 'Production / Internal',
  linkedAuditId: 'AUD-2026-0313-014',
  decisionHash: 'sha256:a1b2c3d4e5f60718293a4b5c6d7e8f90',
  contractHash: 'sha256:f0e9d8c7b6a5948372615049382716aa',
  auditBasis: 'Audit Detail / Rulepack v1.0 / Constitution v2.1',
  reviewedAt: '2026-03-13 08:55 CST',
};

const scopeItems = [
  ['Environment', 'Production'],
  ['Asset Boundary', 'Payment Agent Skill only'],
  ['Revision Scope', 'R-014 only'],
  ['Invocation Boundary', 'Declared execution path only'],
  ['Valid Use Context', 'Internal operations and approved client delivery'],
] as const;

const conditionGroups = [
  {
    title: 'Must Hold',
    items: [
      'Certified revision must remain unchanged from R-014.',
      'Linked audit basis and decision hash must stay current.',
      'Operational monitoring must remain enabled.',
    ],
  },
  {
    title: 'Re-audit Triggers',
    items: [
      'Rulepack or constitution version changes.',
      'New execution path or undeclared capability appears.',
      'Evidence coverage drops below current sufficiency level.',
    ],
  },
  {
    title: 'Invalidation Triggers',
    items: [
      'Permit invalidates on policy mismatch.',
      'Permit invalidates on revision drift.',
      'Permit invalidates on undeclared execution path.',
    ],
  },
];

const basisItems = [
  ['Linked Audit ID', permitData.linkedAuditId],
  ['Audit Result', 'Passed with permit recommendation'],
  ['Decision Hash', permitData.decisionHash],
  ['Contract Hash', permitData.contractHash],
  ['Audit Version', 'Audit v1.0'],
  ['Reviewed At', permitData.reviewedAt],
] as const;

const evidencePolicyItems = [
  ['Evidence Summary', '11 evidence refs / 3 summary-only / 1 restricted'],
  ['Evidence Sufficiency', 'Sufficient'],
  ['Rulepack Version', 'Rulepack v1.0'],
  ['Constitution Version', 'Constitution v2.1'],
  ['Compliance Note', 'Release allowed within declared scope only'],
] as const;

const lifecycleItems: LifecycleItem[] = [
  { label: 'Audit Completed', time: '08:55', actor: 'Audit-01', state: 'done' },
  { label: 'Ready for Permit', time: '09:05', actor: 'Reviewer-02', state: 'done' },
  { label: 'Permit Issued', time: '09:30', actor: 'Compliance-01', state: 'current' },
  { label: 'Active', time: '09:30+', actor: 'System', state: 'current' },
  { label: 'Revoked / Expired / Superseded', time: 'When triggered', state: 'future' },
];

const signatureItems = [
  ['Signed By', 'Compliance-01'],
  ['Signed At', '2026-03-13 09:30 CST'],
  ['Signature Note', 'Permit granted after full audit and basis confirmation.'],
  ['Approval Remarks', 'Approved for production within declared scope only.'],
  ['Release Comments', 'Residual monitoring required during active period.'],
] as const;

const residualRisks = [
  'Monitoring remains mandatory during active lifecycle.',
  'Permit must be re-issued if revision, rulepack or constitution changes.',
  'Undeclared execution paths invalidate this permit immediately.',
];

const getStatusClassName = (status: PermitStatus): string => {
  switch (status) {
    case 'Active':
      return styles.statusActive;
    case 'Pending':
      return styles.statusPending;
    case 'Revoked':
      return styles.statusRevoked;
    case 'Expired':
    case 'Superseded':
      return styles.statusExpired;
    default:
      return '';
  }
};

const PermitPage: React.FC = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const {
    draft,
    setDraft,
    draftIntentHint,
    setDraftIntentHint,
    latestTurn,
    latestTurns,
    activeDecision,
    submitDraft,
    isTyping,
  } = useGovernanceInteraction();
  const copy =
    language === 'zh'
      ? {
          contextEyebrow: '当前输入上下文',
          contextTitle: '这张画布承接 Permit 放行与正式发布决策。',
          contextSummary: '当输入被裁决为 Permit、放行或签发相关动作时，系统会将结果状态和正式凭证承接到这里展示。',
          contextPrompt: '当前确认输入',
          contextStatus: '当前画布',
          contextStatusValue: 'Permit Decision',
          breadcrumb: '发布 / Permit /',
          certificate: '放行凭证',
          labels: { asset: '资产', revision: '修订', effective: '生效时间', signedBy: '签发方', scope: '范围' },
          actions: { export: '导出 Permit', linkedAudit: '查看关联审计', history: '查看历史', revoke: '撤销 Permit' },
          permitGranted: 'Permit 已签发',
          headline: '审计通过不等于放行批准。Permit 才是。',
          decisionSublinePrefix: '该 Permit 绑定到修订',
          decisionSublineSuffix: '、decision hash 与 contract hash。只有在声明范围和条件内才允许放行。',
          decisionHash: 'Decision Hash',
          contractHash: 'Contract Hash',
          releaseScope: '放行范围',
          conditions: '条件',
          auditBasis: '审计依据',
          evidencePolicy: '证据 / 策略依据',
          lifecycle: 'Permit 生命周期',
          signature: '合规签名',
          residualRiskTitle: '残余风险提醒',
          residualRiskNote: 'Permit 不代表零风险。它意味着在声明范围、声明条件和持续监控下允许放行。',
          conditionTitles: { mustHold: '必须满足', reaudit: '重新审计触发器', invalidation: '失效触发器' },
        }
      : {
          contextEyebrow: 'Current input context',
          contextTitle: 'This canvas carries permit release and formal issuance decisions.',
          contextSummary: 'When input resolves into permit, release, or issuance actions, the system carries the result state and formal credential surface here.',
          contextPrompt: 'Confirmed input',
          contextStatus: 'Active canvas',
          contextStatusValue: 'Permit Decision',
          breadcrumb: 'Release / Permit /',
          certificate: 'Permit Certificate',
          labels: { asset: 'Asset', revision: 'Revision', effective: 'Effective', signedBy: 'Signed By', scope: 'Scope' },
          actions: { export: 'Export Permit', linkedAudit: 'View Linked Audit', history: 'View History', revoke: 'Revoke Permit' },
          permitGranted: 'Permit granted',
          headline: 'Audit pass is not release approval. Permit is.',
          decisionSublinePrefix: 'This permit is bound to revision',
          decisionSublineSuffix: ', decision hash and contract hash. Release is allowed only within the declared scope and conditions below.',
          decisionHash: 'Decision Hash',
          contractHash: 'Contract Hash',
          releaseScope: 'Release Scope',
          conditions: 'Conditions',
          auditBasis: 'Audit Basis',
          evidencePolicy: 'Evidence / Policy Basis',
          lifecycle: 'Permit Lifecycle',
          signature: 'Compliance Signature',
          residualRiskTitle: 'Residual Risk Reminder',
          residualRiskNote: 'Permit does not mean zero risk. It means release is allowed within declared scope, under declared conditions, with ongoing monitoring.',
          conditionTitles: { mustHold: 'Must Hold', reaudit: 'Re-audit Triggers', invalidation: 'Invalidation Triggers' },
        };

  const localizedConditionGroups = conditionGroups.map((group) => ({
    ...group,
    title:
      group.title === 'Must Hold'
        ? copy.conditionTitles.mustHold
        : group.title === 'Re-audit Triggers'
          ? copy.conditionTitles.reaudit
          : copy.conditionTitles.invalidation,
  }));

  const quickActions: ComposerAction[] = [
    {
      label: language === 'zh' ? '导入外部 Skill' : 'Import external skill',
      prompt: language === 'zh' ? '审查这个外部 Skill 是否可以安装' : 'Vet whether this external skill can be installed',
      icon: '↘',
      intentHint: 'vetting',
    },
    {
      label: language === 'zh' ? '审查 Revision' : 'Review revision',
      prompt: language === 'zh' ? '解释为什么当前 Revision 被阻断' : 'Explain why the current revision is blocked',
      icon: '◎',
      intentHint: 'audit',
    },
    {
      label: language === 'zh' ? '申请 Permit' : 'Request permit',
      prompt: language === 'zh' ? '为这个 Skill 申请 Permit 放行' : 'Request permit release for this skill',
      icon: '◆',
      intentHint: 'permit',
    },
  ];

  const historyItems: ContextCanvasHistoryItem[] = latestTurns.map((turn) => ({
    id: turn.id,
    input: turn.userInput,
    state: turn.intent === 'unknown' ? copy.contextStatusValue : turn.intent,
  }));

  const slotConfig = useMemo(
    () => ({
      variant: 'context' as const,
      decision: activeDecision,
      confirmedValue: latestTurn?.userInput,
      showCanvas: Boolean(latestTurn && !isTyping),
      showHistory: Boolean(!isTyping && historyItems.length > 1),
      history: {
        title: copy.contextPrompt,
        subtitle: copy.contextStatusValue,
        items: historyItems,
      },
      consoleHeader: {
        eyebrow: copy.contextEyebrow,
        title: copy.contextTitle,
        meta: copy.contextStatusValue,
      },
      consoleHint: copy.contextSummary,
      composer: {
        value: draft,
        onChange: setDraft,
        onSubmit: async () => {
          await submitDraft({ intentHint: draftIntentHint });
        },
        placeholder:
          language === 'zh'
            ? '继续确认 Permit、放行条件、残余风险或签发动作。'
            : 'Continue with permit conditions, residual risk, or issuance actions.',
        submitLabel: copy.actions.export,
        addAttachmentLabel: language === 'zh' ? '添加附件' : 'Add attachment',
        imageActionLabel: language === 'zh' ? '图片' : 'Image',
        fileActionLabel: language === 'zh' ? '文件' : 'File',
        enterKeyLabel: 'Enter',
        enterLabel: language === 'zh' ? '提交' : 'Submit',
        shiftEnterKeyLabel: 'Shift+Enter',
        newlineLabel: language === 'zh' ? '换行' : 'New line',
        separatorLabel: '·',
        imageAttachedLabel: language === 'zh' ? '已附加图片' : 'Image attached',
        fileAttachedLabel: language === 'zh' ? '已附加文件' : 'File attached',
        quickActions,
        onQuickActionSelect: (action: ComposerAction) => {
          setDraft(action.prompt);
          setDraftIntentHint(action.intentHint ?? 'unknown');
        },
        intentTabs: [
          { key: 'vetting' as const, label: language === 'zh' ? '导入外部 Skill' : 'Import External Skill' },
          { key: 'audit' as const, label: language === 'zh' ? '审查 Revision' : 'Review Revision' },
          { key: 'permit' as const, label: language === 'zh' ? '申请 Permit' : 'Request Permit' },
        ],
        selectedIntent: draftIntentHint,
        onIntentSelect: setDraftIntentHint,
      },
      onPrimaryAction: (decision: typeof activeDecision) => {
        if (decision.routeTarget && latestTurn?.userInput) {
          navigate(`${decision.routeTarget}?prompt=${encodeURIComponent(latestTurn.userInput)}`);
        }
      },
      onAlternativeSelect: (intent: 'vetting' | 'audit' | 'permit') => {
        if (!latestTurn?.userInput) return;
        navigate(`${INTENT_ROUTE_MAP[intent]}?prompt=${encodeURIComponent(latestTurn.userInput)}`);
      },
    }),
    [
      activeDecision,
      copy.actions.export,
      copy.contextEyebrow,
      copy.contextPrompt,
      copy.contextStatusValue,
      copy.contextSummary,
      copy.contextTitle,
      draft,
      draftIntentHint,
      historyItems,
      isTyping,
      language,
      latestTurn?.userInput,
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
      <div className={styles.breadcrumb}>{copy.breadcrumb} {permitData.permitId}</div>

      <section className={styles.headerCard}>
        <div className={styles.headerTop}>
          <div>
            <p className={styles.eyebrow}>{copy.certificate}</p>
            <h1 className={styles.pageTitle}>{permitData.permitId}</h1>
          </div>
          <div className={`${styles.statusBadge} ${getStatusClassName(permitData.status)}`}>
            {permitData.status}
          </div>
        </div>

        <div className={styles.headerGrid}>
          <div className={styles.headerField}>
            <span className={styles.label}>{copy.labels.asset}</span>
            <span className={styles.value}>{permitData.assetName}</span>
          </div>
          <div className={styles.headerField}>
            <span className={styles.label}>{copy.labels.revision}</span>
            <span className={styles.value}>{permitData.revision}</span>
          </div>
          <div className={styles.headerField}>
            <span className={styles.label}>{copy.labels.effective}</span>
            <span className={styles.value}>{permitData.effectiveDate}</span>
          </div>
          <div className={styles.headerField}>
            <span className={styles.label}>{copy.labels.signedBy}</span>
            <span className={styles.value}>{permitData.signedBy}</span>
          </div>
          <div className={styles.headerField}>
            <span className={styles.label}>{copy.labels.scope}</span>
            <span className={styles.value}>{permitData.scope}</span>
          </div>
        </div>

        <div className={styles.actionRow}>
          <button className={styles.primaryGhost}>{copy.actions.export}</button>
          <button className={styles.secondaryGhost}>{copy.actions.linkedAudit}</button>
          <button className={styles.secondaryGhost}>{copy.actions.history}</button>
          <button className={styles.dangerGhost}>{copy.actions.revoke}</button>
        </div>
      </section>

      <section className={styles.decisionCard}>
        <p className={styles.decisionState}>{copy.permitGranted}</p>
        <h2 className={styles.decisionHeadline}>{copy.headline}</h2>
        <p className={styles.decisionSubline}>
          {copy.decisionSublinePrefix} {permitData.revision}{copy.decisionSublineSuffix}
        </p>
        <div className={styles.bindingStrip}>
          <span>{copy.decisionHash}: {permitData.decisionHash.slice(0, 20)}...</span>
          <span>{copy.contractHash}: {permitData.contractHash.slice(0, 20)}...</span>
        </div>
      </section>

      <section className={styles.twoColumnGrid}>
        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.releaseScope}</h3>
          <dl className={styles.definitionList}>
            {scopeItems.map(([key, value]) => (
              <div key={key} className={styles.definitionRow}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>

        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.conditions}</h3>
          <div className={styles.conditionStack}>
            {localizedConditionGroups.map((group) => (
              <section key={group.title} className={styles.conditionBlock}>
                <h4>{group.title}</h4>
                <ul>
                  {group.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </article>
      </section>

      <section className={styles.twoColumnGrid}>
        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.auditBasis}</h3>
          <dl className={styles.definitionList}>
            {basisItems.map(([key, value]) => (
              <div key={key} className={styles.definitionRow}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>

        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.evidencePolicy}</h3>
          <dl className={styles.definitionList}>
            {evidencePolicyItems.map(([key, value]) => (
              <div key={key} className={styles.definitionRow}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>

      <section className={styles.twoColumnGrid}>
        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.lifecycle}</h3>
          <ol className={styles.timeline}>
            {lifecycleItems.map((item) => (
              <li key={item.label} className={styles.timelineItem}>
                <span className={`${styles.timelineDot} ${styles[`timeline${item.state[0].toUpperCase()}${item.state.slice(1)}`]}`} />
                <div className={styles.timelineBody}>
                  <div className={styles.timelineHead}>
                    <strong>{item.label}</strong>
                    <span>{item.time}</span>
                  </div>
                  {item.actor && <p>{item.actor}</p>}
                </div>
              </li>
            ))}
          </ol>
        </article>

        <article className={styles.card}>
          <h3 className={styles.cardTitle}>{copy.signature}</h3>
          <dl className={styles.definitionList}>
            {signatureItems.map(([key, value]) => (
              <div key={key} className={styles.definitionRow}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>
      </section>

      <section className={styles.riskCard}>
        <h3 className={styles.cardTitle}>{copy.residualRiskTitle}</h3>
        <ul className={styles.riskList}>
          {residualRisks.map((risk) => (
            <li key={risk}>{risk}</li>
          ))}
        </ul>
        <p className={styles.riskNote}>{copy.residualRiskNote}</p>
      </section>
    </main>
  );
};

export default PermitPage;
