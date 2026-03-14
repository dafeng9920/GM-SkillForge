import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../app/i18n';
import styles from './VettingPage.module.css';

const VettingPermitDecisionPage: React.FC = () => {
  const { language } = useLanguage();
  const copy =
    language === 'zh'
      ? {
          eyebrow: '审查 Permit 决策',
          title: 'VTP-2026-0313-001',
          subtitle: '外部 Skill 包 · pkg-fp-2026-0313-001 · Compliance 签发',
          status: '条件允许',
          lead: '审查不等于安装批准。Permit 才是。',
          decisionText: '这个 Permit 绑定到导入修订和关联裁决之上。它是正式的、修订绑定的，并且受条件约束。',
          approvedScope: '批准范围',
          conditionsTitle: '条件',
          linkedBasisTitle: '关联依据',
          risksTitle: '残余风险',
          risksBody: '条件 Permit 不会消除风险。导入 Skill 仍然处于受监控的摄入控制之下，直到完成发布审查。',
          lifecycleTitle: '生命周期',
          stickyTitle: 'Permit 状态：条件允许',
          stickyBody: '绑定修订 pkg-fp-2026-0313-001 与关联裁决报告',
          issuePermit: '签发条件 Permit',
          manualApproval: '要求人工批准',
          denyInstall: '拒绝安装',
          openReport: '打开关联报告',
          scopeItems: [
            ['允许环境', '仅限内部审查工作区'],
            ['允许操作员', '已批准的摄入审查员与合规操作员'],
            ['允许使用场景', '安装前评估与受控验证'],
            ['允许动作类别', '读取、检查、打包审查、人工批准路径'],
          ],
          conditions: [
            '高风险动作必须人工批准。',
            '修订变化后必须重新审查。',
            '权限漂移会导致 Permit 失效。',
            '没有明确发布审查就不能进入生产发布。',
          ],
          linkedBasis: [
            ['报告 ID', 'VET-REP-2026-0313-001'],
            ['风险等级', '高'],
            ['安装闸门', '条件'],
            ['裁决状态', '需人工批准'],
            ['包指纹', 'pkg-fp-2026-0313-001'],
          ],
          lifecycle: ['已导入', '已审查', '已裁决', 'Permit 待定', '条件允许'],
        }
      : {
          eyebrow: 'Vetting Permit Decision',
          title: 'VTP-2026-0313-001',
          subtitle: 'External Skill Package · pkg-fp-2026-0313-001 · Compliance issuer',
          status: 'Conditionally Allowed',
          lead: 'Vetting is not installation approval. Permit is.',
          decisionText: 'This permit is bound to the imported revision and linked adjudication. It remains formal, revision-bound and subject to conditions.',
          approvedScope: 'Approved scope',
          conditionsTitle: 'Conditions',
          linkedBasisTitle: 'Linked basis',
          risksTitle: 'Residual risks',
          risksBody: 'Conditional permit does not erase risk. Imported skill remains under monitored intake control until release review.',
          lifecycleTitle: 'Lifecycle',
          stickyTitle: 'Permit status: Conditionally Allowed',
          stickyBody: 'Bound to revision pkg-fp-2026-0313-001 and linked adjudication report',
          issuePermit: 'Issue Conditional Permit',
          manualApproval: 'Require Manual Approval',
          denyInstall: 'Deny Installation',
          openReport: 'Open Linked Report',
          scopeItems: [
            ['Allowed environment', 'Internal review workspace only'],
            ['Allowed operators', 'Approved intake reviewers and compliance operators'],
            ['Allowed use context', 'Pre-install evaluation and controlled validation'],
            ['Allowed action classes', 'Read, inspect, package review, manual approval path'],
          ],
          conditions: [
            'Manual approval required for high-risk actions.',
            'Re-vet required on revision change.',
            'Permit invalidates on permission drift.',
            'No production rollout without explicit release review.',
          ],
          linkedBasis: [
            ['Report ID', 'VET-REP-2026-0313-001'],
            ['Risk tier', 'High'],
            ['Install gate', 'Conditional'],
            ['Adjudication status', 'Manual approval required'],
            ['Package fingerprint', 'pkg-fp-2026-0313-001'],
          ],
          lifecycle: ['Imported', 'Vetted', 'Adjudicated', 'Permit Pending', 'Conditionally Allowed'],
        };

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

      <section className={styles.decisionBlock}>
        <p className={styles.decisionLead}>{copy.lead}</p>
        <p className={styles.decisionText}>{copy.decisionText}</p>
      </section>

      <section className={styles.twoColumn}>
        <article className={styles.card}>
          <h2>{copy.approvedScope}</h2>
          <dl className={styles.definitionList}>
            {copy.scopeItems.map(([label, value]) => (
              <div key={label} className={styles.definitionRow}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>
        <article className={styles.card}>
          <h2>{copy.conditionsTitle}</h2>
          <ul className={styles.list}>
            {copy.conditions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className={styles.twoColumn}>
        <article className={styles.card}>
          <h2>{copy.linkedBasisTitle}</h2>
          <dl className={styles.definitionList}>
            {copy.linkedBasis.map(([label, value]) => (
              <div key={label} className={styles.definitionRow}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </article>
        <article className={styles.card}>
          <h2>{copy.risksTitle}</h2>
          <p>{copy.risksBody}</p>
        </article>
      </section>

      <section className={styles.card}>
        <h2>{copy.lifecycleTitle}</h2>
        <div className={styles.timeline}>
          {copy.lifecycle.map((item) => (
            <div key={item} className={styles.timelineStep}>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </section>

      <footer className={styles.stickyBar}>
        <div>
          <strong>{copy.stickyTitle}</strong>
          <p>{copy.stickyBody}</p>
        </div>
        <div className={styles.ctaRow}>
          <button className={styles.primaryButton}>{copy.issuePermit}</button>
          <button className={styles.secondaryButton}>{copy.manualApproval}</button>
          <button className={styles.dangerButton}>{copy.denyInstall}</button>
          <Link to="/intake/vetting/report" className={styles.secondaryButtonLink}>
            {copy.openReport}
          </Link>
        </div>
      </footer>
    </main>
  );
};

export default VettingPermitDecisionPage;
