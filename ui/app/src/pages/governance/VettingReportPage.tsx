import React, { useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import type { ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import { useGovernanceCanvasSlot } from '../../components/governance/GovernanceCanvasSlot';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { INTENT_ROUTE_MAP, useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import styles from './VettingPage.module.css';

const VettingReportPage: React.FC = () => {
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
          contextTitle: '这张画布展示外部 Skill 审查的正式裁决结果。',
          contextSummary: '当输入被裁决为外部资产引入或安装前判断后，系统会把结果承接到这里，而不是让用户重新理解一个新页面。',
          contextPrompt: '当前确认输入',
          contextStatus: '当前画布',
          contextStatusValue: 'Vetting Report',
          eyebrow: '审查报告',
          title: '外部 Skill 包',
          subtitle: '仓库导入 · github.com/example/external-skill · pkg-fp-2026-0313-001',
          status: '需人工批准',
          summaryCards: [
            ['最终建议', '需人工批准'],
            ['风险等级', '高'],
            ['安装闸门', '条件'],
          ],
          boundaryTitle: '权限边界',
          execution: 'Execution',
          executionBody: '可以导入并准备摄入包，但不能批准安装。',
          audit: 'Audit',
          auditBody: '可以裁决红线、可修复缺口和安装闸门状态。',
          compliance: 'Compliance',
          complianceBody: '可以签发 Permit、附加条件，或拒绝进入受管流程。',
          sourceTrust: '来源可信度',
          sourceTrustBody: '仓库来源已知，但尚未清理到可自动安装。',
          capabilitySurface: '能力边界面',
          capabilitySurfaceBody: '导入包申请的操作能力超出当前默认摄入策略。',
          redlineFindings: '红线发现',
          redlineFindingsBody: '2 项硬阻断在任何 Permit 被考虑之前都需要明确裁决。',
          permissionFit: '权限匹配',
          permissionFitBody: '声明权限范围与允许的操作员上下文之间仍有 3 项可修复不匹配。',
          gapSummary: '缺口摘要',
          gapSummaryBody: '2 条红线 · 3 个可修复缺口 · 已具备导出关联报告包。',
          releaseReadiness: '发布准备度',
          releaseReadinessBody: '尚未达到安装批准条件。只有在修复评估后才可进入人工批准路径。',
          stickyTitle: '当前决策：需人工批准',
          stickyBody: '2 条红线 · 3 个可修复缺口 · 安装闸门仍为条件状态',
          openFindings: '打开发现',
          reviewGaps: '审查缺口',
          exportPack: '导出审查包',
          submitApproval: '提交审批',
          denyIntake: '拒绝摄入',
        }
      : {
          contextEyebrow: 'Current input context',
          contextTitle: 'This canvas shows the formal adjudication result for external skill vetting.',
          contextSummary: 'When the request resolves into external intake or pre-install review, the system carries the result here instead of forcing the user to re-learn a new page.',
          contextPrompt: 'Confirmed input',
          contextStatus: 'Active canvas',
          contextStatusValue: 'Vetting Report',
          eyebrow: 'Vetting Report',
          title: 'External Skill Package',
          subtitle: 'Repo import · github.com/example/external-skill · pkg-fp-2026-0313-001',
          status: 'Manual Approval Required',
          summaryCards: [
            ['Final Recommendation', 'Manual Approval Required'],
            ['Risk Tier', 'High'],
            ['Install Gate', 'Conditional'],
          ],
          boundaryTitle: 'Authority boundary',
          execution: 'Execution',
          executionBody: 'Can import and prepare intake packages, not approve installation.',
          audit: 'Audit',
          auditBody: 'Can adjudicate red lines, fixable gaps and install gate status.',
          compliance: 'Compliance',
          complianceBody: 'Can issue permit, apply conditions or deny entry into the governed pipeline.',
          sourceTrust: 'Source Trust',
          sourceTrustBody: 'Repository source is known but not yet cleared for automatic installation.',
          capabilitySurface: 'Capability Surface',
          capabilitySurfaceBody: 'Imported package requests operational actions that exceed the current default intake policy.',
          redlineFindings: 'Redline Findings',
          redlineFindingsBody: '2 hard blockers require explicit adjudication before any permit can be considered.',
          permissionFit: 'Permission Fit',
          permissionFitBody: '3 fixable mismatches remain between declared permission scope and allowed operator context.',
          gapSummary: 'Gap Summary',
          gapSummaryBody: '2 red lines · 3 fixable gaps · linked report package ready for export.',
          releaseReadiness: 'Release Readiness',
          releaseReadinessBody: 'Not ready for installation approval. Eligible only for manual approval path after remediation review.',
          stickyTitle: 'Current decision: Manual approval required',
          stickyBody: '2 red lines · 3 fixable gaps · install gate remains conditional',
          openFindings: 'Open Findings',
          reviewGaps: 'Review Gaps',
          exportPack: 'Export Vetting Pack',
          submitApproval: 'Submit for Approval',
          denyIntake: 'Deny Intake',
        };

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
      prompt: language === 'zh' ? '把审查结果提交到 Permit 裁决' : 'Submit this review into permit adjudication',
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
            ? '继续追问红线、缺口、权限匹配或下一步动作。'
            : 'Continue with red lines, gaps, permission fit, or next action questions.',
        submitLabel: copy.submitApproval,
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
      copy.contextEyebrow,
      copy.contextPrompt,
      copy.contextStatusValue,
      copy.contextSummary,
      copy.contextTitle,
      copy.submitApproval,
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
      <section className={styles.headerCard}>
        <div>
          <p className={styles.eyebrow}>{copy.eyebrow}</p>
          <h1 className={styles.title}>{copy.title}</h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>
        </div>
        <span className={styles.statusBadge}>{copy.status}</span>
      </section>

      <section className={styles.metricGrid}>
        {copy.summaryCards.map(([label, value]) => (
          <article key={label} className={styles.metricCard}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>{copy.boundaryTitle}</h2>
        </div>
        <div className={styles.authorityGrid}>
          <div className={styles.authorityCard}>
            <strong>{copy.execution}</strong>
            <p>{copy.executionBody}</p>
          </div>
          <div className={styles.authorityCard}>
            <strong>{copy.audit}</strong>
            <p>{copy.auditBody}</p>
          </div>
          <div className={styles.authorityCard}>
            <strong>{copy.compliance}</strong>
            <p>{copy.complianceBody}</p>
          </div>
        </div>
      </section>

      <section className={styles.twoColumn}>
        <article className={styles.card}>
          <h2>{copy.sourceTrust}</h2>
          <p>{copy.sourceTrustBody}</p>
        </article>
        <article className={styles.card}>
          <h2>{copy.capabilitySurface}</h2>
          <p>{copy.capabilitySurfaceBody}</p>
        </article>
        <article className={styles.card}>
          <h2>{copy.redlineFindings}</h2>
          <p>{copy.redlineFindingsBody}</p>
        </article>
        <article className={styles.card}>
          <h2>{copy.permissionFit}</h2>
          <p>{copy.permissionFitBody}</p>
        </article>
      </section>

      <section className={styles.twoColumn}>
        <article className={styles.card}>
          <h2>{copy.gapSummary}</h2>
          <p>{copy.gapSummaryBody}</p>
        </article>
        <article className={styles.card}>
          <h2>{copy.releaseReadiness}</h2>
          <p>{copy.releaseReadinessBody}</p>
        </article>
      </section>

      <footer className={styles.stickyBar}>
        <div>
          <strong>{copy.stickyTitle}</strong>
          <p>{copy.stickyBody}</p>
        </div>
        <div className={styles.ctaRow}>
          <button className={styles.secondaryButton}>{copy.openFindings}</button>
          <button className={styles.secondaryButton}>{copy.reviewGaps}</button>
          <button className={styles.secondaryButton}>{copy.exportPack}</button>
          <Link to="/release/vetting-permit" className={styles.primaryButtonLink}>
            {copy.submitApproval}
          </Link>
          <button className={styles.dangerButton}>{copy.denyIntake}</button>
        </div>
      </footer>
    </main>
  );
};

export default VettingReportPage;
