import React, { useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import type { ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import { useGovernanceCanvasSlot } from '../../components/governance/GovernanceCanvasSlot';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { INTENT_ROUTE_MAP, useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import { useGovernancePromptQuerySync } from '../../features/governanceInteraction/useGovernancePromptQuerySync';
import styles from './VettingPage.module.css';

const VettingHomePage: React.FC = () => {
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
  useGovernancePromptQuerySync({ intentHint: 'vetting' });
  const copy =
    language === 'zh'
      ? {
          contextEyebrow: '当前输入上下文',
          contextTitle: '系统已将当前请求带入外部 Skill 审查。',
          contextSummary: '这张画布承接外部来源、安装前判断和入口闸门审查。输入框中的意图会先经过裁决，再在这里展开为审查动作。',
          contextPrompt: '当前确认输入',
          contextStatus: '当前画布',
          contextStatusValue: 'External Skill Vetting',
          eyebrow: '入口闸门',
          title: '在外部 Skill 进入系统前先完成审查',
          subtitle: '从链接、仓库或压缩包导入外部 Skill，并在安装或发布之前进入受控审查流程。',
          primary: '开始审查',
          secondary: '查看示例报告',
          process: ['导入', '审查', '裁决', '许可 / 拒绝'],
          methodsTitle: '导入方式',
          methods: ['从链接导入', '从 Git 仓库导入', '上传 ZIP / 文件夹'],
          methodsBody: '把外部 Skill 带入受控摄入路径。',
          formTitle: '启动一次审查',
          source: '来源',
          nameOverride: 'Skill 名称覆盖',
          notes: '摄入说明',
          defaultSource: 'https://repo.example.com/external-skill',
          defaultName: '外部 Skill 包',
          defaultNotes: '提交为安装前的外部摄入审查。',
          warning: '在完成审查与裁决前，所有外部 Skill 都视为不受信任资产。',
          checksTitle: '审查会检查什么',
          checks: ['来源可信度', '红线扫描', '权限匹配', '风险裁决', '安装闸门'],
          recentTitle: '最近审查记录',
          openSample: '打开示例报告',
          headers: ['Skill', '来源', '风险', '闸门', '决策', '时间'],
          runs: [
            ['Partner Search Skill', '仓库', '高', '条件', '需人工批准', '12 分钟前'],
            ['FAQ Helper Package', 'ZIP', '低', '开放', '允许', '32 分钟前'],
            ['External Triage Agent', '链接', '中', '阻断', '拒绝', '1 小时前'],
          ],
        }
      : {
          contextEyebrow: 'Current input context',
          contextTitle: 'The system has brought the active request into external skill vetting.',
          contextSummary: 'This canvas handles external sources, pre-install review, and entry gating. Input is adjudicated first and then expanded here into vetting actions.',
          contextPrompt: 'Confirmed input',
          contextStatus: 'Active canvas',
          contextStatusValue: 'External Skill Vetting',
          eyebrow: 'Intake Gate',
          title: 'Vet External Skills Before They Enter Your System',
          subtitle: 'Import external skills from links, repos, or packages and move them through a governed vetting flow before installation or release.',
          primary: 'Start Vetting',
          secondary: 'View Sample Report',
          process: ['Import', 'Vet', 'Adjudicate', 'Permit / Deny'],
          methodsTitle: 'Import methods',
          methods: ['Import from URL', 'Import from Git Repo', 'Upload ZIP / Folder'],
          methodsBody: 'Bring an external skill into the governed intake path.',
          formTitle: 'Start a vetting run',
          source: 'Source',
          nameOverride: 'Skill name override',
          notes: 'Intake notes',
          defaultSource: 'https://repo.example.com/external-skill',
          defaultName: 'External Skill Package',
          defaultNotes: 'Submitted for external intake review before internal installation.',
          warning: 'External skills are treated as untrusted until vetted and adjudicated.',
          checksTitle: 'What vetting checks',
          checks: ['Source Trust', 'Redline Scan', 'Permission Fit', 'Risk Adjudication', 'Install Gate'],
          recentTitle: 'Recent vetting runs',
          openSample: 'Open sample report',
          headers: ['Skill', 'Source', 'Risk', 'Gate', 'Decision', 'Time'],
          runs: [
            ['Partner Search Skill', 'Repo', 'High', 'Conditional', 'Manual Approval Required', '12 min ago'],
            ['FAQ Helper Package', 'ZIP', 'Low', 'Open', 'Allowed', '32 min ago'],
            ['External Triage Agent', 'URL', 'Medium', 'Blocked', 'Denied', '1 h ago'],
          ],
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
      prompt: language === 'zh' ? '检查当前 Revision 是否已经准备好申请许可' : 'Check whether the current revision is ready for permit review',
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
            ? '继续描述外部 Skill 来源、包指纹或安装前判断。'
            : 'Continue with source, package fingerprint, or pre-install review details.',
        submitLabel: copy.primary,
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
      copy.primary,
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
      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>{copy.eyebrow}</p>
          <h1 className={styles.title}>{copy.title}</h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>
          <div className={styles.ctaRow}>
            <button className={styles.primaryButton}>{copy.primary}</button>
            <Link to="/intake/vetting/report" className={styles.secondaryButtonLink}>
              {copy.secondary}
            </Link>
          </div>
          <div className={styles.processStrip}>
            {copy.process.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.twoColumn}>
        <article className={styles.card}>
          <h2>{copy.methodsTitle}</h2>
          <div className={styles.stack}>
            {copy.methods.map((item) => (
              <div key={item} className={styles.methodCard}>
                <strong>{item}</strong>
                <p>{copy.methodsBody}</p>
              </div>
            ))}
          </div>
        </article>

        <article className={styles.card}>
          <h2>{copy.formTitle}</h2>
          <div className={styles.formStack}>
            <label>
              <span>{copy.source}</span>
              <input type="text" defaultValue={copy.defaultSource} />
            </label>
            <label>
              <span>{copy.nameOverride}</span>
              <input type="text" defaultValue={copy.defaultName} />
            </label>
            <label>
              <span>{copy.notes}</span>
              <textarea rows={4} defaultValue={copy.defaultNotes} />
            </label>
            <Link to="/intake/vetting/report" className={styles.primaryButtonLink}>
              {copy.primary}
            </Link>
          </div>
        </article>
      </section>

      <section className={styles.warningStrip}>{copy.warning}</section>

      <section className={styles.card}>
        <h2>{copy.checksTitle}</h2>
        <div className={styles.checkGrid}>
          {copy.checks.map((item) => (
            <div key={item} className={styles.checkCard}>
              <strong>{item}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>{copy.recentTitle}</h2>
          <Link to="/intake/vetting/report" className={styles.inlineLink}>
            {copy.openSample}
          </Link>
        </div>
        <div className={styles.table}>
          <div className={styles.tableHead}>
            {copy.headers.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
          {copy.runs.map((row) => (
            <div key={row[0]} className={styles.tableRow}>
              {row.map((cell) => (
                <span key={cell}>{cell}</span>
              ))}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default VettingHomePage;
