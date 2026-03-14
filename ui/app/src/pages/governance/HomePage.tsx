import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import { ContextCanvasHost, type ContextCanvasHistoryItem } from '../../components/governance/ContextCanvasHost';
import type { ComposerAction } from '../../components/governance/GovernComposer';
import { INTENT_ROUTE_MAP, useGovernanceInteraction } from '../../features/governanceInteraction/interaction';
import styles from './HomePage.module.css';

const COPY = {
  zh: {
    eyebrow: 'GM-SkillForge',
    title: '从生成到治理',
    subtitle: '描述你要引入、审查或放行的 Skill，系统会把它带入正确的治理路径。',
    placeholder: '例如：审查这个外部 Skill 是否可以安装',
    start: '开始',
    addAttachment: '添加附件',
    imageAction: '图片',
    fileAction: '文件',
    enterHint: 'Enter 提交 · Shift+Enter 换行',
    enterKey: 'Enter',
    shiftEnterKey: 'Shift+Enter',
    separator: '·',
    imageAttached: '已附加图片',
    fileAttached: '已附加文件',
    historyTitle: '已确认的输入记录',
    clarificationTitle: '需要进一步确认',
  },
  en: {
    eyebrow: 'GM-SkillForge',
    title: 'From Generated to Governed',
    subtitle: 'Describe the skill you want to intake, audit, or release, and the system will route it into the correct governed flow.',
    placeholder: 'For example: vet whether this external skill can be installed',
    start: 'Start',
    addAttachment: 'Add attachment',
    imageAction: 'Image',
    fileAction: 'File',
    enterHint: 'Enter to submit · Shift+Enter for newline',
    enterKey: 'Enter',
    shiftEnterKey: 'Shift+Enter',
    separator: '·',
    imageAttached: 'Image attached',
    fileAttached: 'File attached',
    historyTitle: 'Confirmed input history',
    clarificationTitle: 'Clarification required',
  },
} as const;

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const {
    draft,
    setDraft,
    latestTurn,
    latestTurns,
    latestDecision,
    submitDraft,
    isTyping,
    setDraftIntentHint,
  } = useGovernanceInteraction();
  const copy = COPY[language];

  const quickActions = useMemo<ComposerAction[]>(
    () => ([
      {
        label: language === 'zh' ? '导入外部 Skill' : 'Import external skill',
        prompt: language === 'zh' ? '审查这个外部 Skill 是否可以安装' : 'Vet whether this external skill can be installed',
        icon: '↘',
        intentHint: 'vetting',
      },
      {
        label: language === 'zh' ? '审查 Revision' : 'Review revision',
        prompt: language === 'zh' ? '检查当前 Revision 是否已经准备好申请许可' : 'Check whether this revision is ready for permit review',
        icon: '◎',
        intentHint: 'audit',
      },
      {
        label: language === 'zh' ? '申请 Permit' : 'Request permit',
        prompt: language === 'zh' ? '为这个 Skill 申请 Permit 放行' : 'Request permit release for this skill',
        icon: '◆',
        intentHint: 'permit',
      },
    ]),
    [language],
  );

  const confirmedPrompt = latestTurn?.userInput ?? '';
  const historyItems = useMemo<ContextCanvasHistoryItem[]>(
    () =>
      latestTurns.map((turn) => ({
        id: turn.id,
        input: turn.userInput,
        state: turn.intent === 'unknown' ? copy.clarificationTitle : turn.intent,
      })),
    [copy.clarificationTitle, latestTurns],
  );

  return (
    <main className={styles.page}>
      <section className={styles.stage}>
        <div className={styles.heroContent}>
          <p className={styles.eyebrow}>{copy.eyebrow}</p>
          <h1 className={styles.title}>{copy.title}</h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>

        </div>

        <div className={styles.bottomDock}>
          <div className={styles.commandRow}>
            <ContextCanvasHost
              variant="home"
              language={language}
              decision={latestDecision ?? {
                intent: 'unknown',
                canvas: 'home',
                confidence: 'low',
                requiresClarification: false,
                routeTarget: null,
              }}
              confirmedValue={confirmedPrompt}
              showCanvas={Boolean(confirmedPrompt && !isTyping && latestDecision)}
              showHistory={Boolean(!isTyping && historyItems.length > 1)}
              history={{
                title: copy.historyTitle,
                items: historyItems,
              }}
              composer={{
                value: draft,
                onChange: setDraft,
                onSubmit: () => {
                  submitDraft();
                },
                placeholder: copy.placeholder,
                submitLabel: copy.start,
                addAttachmentLabel: copy.addAttachment,
                imageActionLabel: copy.imageAction,
                fileActionLabel: copy.fileAction,
                enterKeyLabel: copy.enterKey,
                enterLabel: copy.enterHint.split('·')[0].replace(copy.enterKey, '').trim(),
                shiftEnterKeyLabel: copy.shiftEnterKey,
                newlineLabel: copy.enterHint.split('·')[1].replace(copy.shiftEnterKey, '').trim(),
                separatorLabel: copy.separator,
                imageAttachedLabel: copy.imageAttached,
                fileAttachedLabel: copy.fileAttached,
                quickActions,
                onQuickActionSelect: (action) => {
                  setDraft(action.prompt);
                  setDraftIntentHint(action.intentHint ?? 'unknown');
                },
              }}
              onPrimaryAction={(decision) => {
                if (!decision.routeTarget || !confirmedPrompt) return;
                navigate(`${decision.routeTarget}?prompt=${encodeURIComponent(confirmedPrompt)}`);
              }}
              onAlternativeSelect={(intent) => {
                if (!confirmedPrompt) return;
                navigate(`${INTENT_ROUTE_MAP[intent]}?prompt=${encodeURIComponent(confirmedPrompt)}`);
              }}
            />
          </div>
        </div>
      </section>
    </main>
  );
};

export default HomePage;
